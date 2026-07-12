"""Upload route pipeline."""
import os
import time
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from core import ocr, language, extractor, classifier, lsi, triage_card
from db import neo4j_client

router = APIRouter()

@router.post("/")
async def process_upload(
    file: UploadFile = File(...),
    exam_name: str = Form(...),
    exam_date: str = Form(...),
    source_platform: str = Form("unknown"),
    hours_to_exam: float = Form(24.0)
):
    start_total = time.time()
    
    # 1. Save uploaded file to /tmp/<uuid>.<ext>
    t0 = time.time()
    ext = os.path.splitext(file.filename or "")[1]
    tmp_path = f"/tmp/{uuid.uuid4()}{ext}"
    os.makedirs("/tmp", exist_ok=True)
    
    try:
        with open(tmp_path, "wb") as f:
            f.write(await file.read())
        print(f"Step 1: Save uploaded file - {time.time() - t0:.3f}s")
        
        # 2. Call ocr.extract_text(path)
        t0 = time.time()
        try:
            raw_text = ocr.extract_text(tmp_path)
        except ValueError as e:
            return JSONResponse(
                status_code=422,
                content={"error": "OCR failed", "detail": str(e)}
            )
        print(f"Step 2: ocr.extract_text - {time.time() - t0:.3f}s")
        
        # 3. Call language.detect_and_translate(raw_text)
        t0 = time.time()
        language_result = language.detect_and_translate(raw_text)
        translated_text = language_result["translated_text"]
        print(f"Step 3: language.detect_and_translate - {time.time() - t0:.3f}s")
        
        # 4. Call extractor.extract_questions(translated_text)
        t0 = time.time()
        questions = extractor.extract_questions(translated_text)
        print(f"Step 4: extractor.extract_questions - {time.time() - t0:.3f}s")
        
        # 5. Call classifier.classify_content(translated_text[:1000])
        t0 = time.time()
        classification_res = classifier.classify_content(translated_text[:1000])
        print(f"Step 5: classifier.classify_content - {time.time() - t0:.3f}s")
        
        # 6. Build signal dict for LSI
        t0 = time.time()
        signal_dict = {
            "question_count": len(questions),
            "hours_to_exam": hours_to_exam,
            "source_platform": source_platform,
            "ghost_paper_match": classification_res.get("classification") == "ghost_paper",
            "spread_count": 0,
            "classification": classification_res.get("classification", "unclear")
        }
        print(f"Step 6: Build signal dict for LSI - {time.time() - t0:.3f}s")
        
        # 7. Call lsi.compute_lsi(signal_dict)
        t0 = time.time()
        lsi_res = lsi.compute_lsi(signal_dict)
        print(f"Step 7: lsi.compute_lsi - {time.time() - t0:.3f}s")
        
        # 8. Generate signal_id
        t0 = time.time()
        signal_id = str(uuid.uuid4())
        print(f"Step 8: Generate signal_id - {time.time() - t0:.3f}s")
        
        # 9. Call neo4j_client.create_signal_node
        t0 = time.time()
        temp_card = {
            "signal_id": signal_id,
            "exam_event": exam_name,
            "exam_date": exam_date,
            "lsi_score": lsi_res.get("lsi_score"),
            "triage_level": lsi_res.get("triage_level"),
            "classification": classification_res.get("classification"),
            "source_platform": source_platform,
            "question_count": len(questions),
            "original_language": language_result.get("original_language"),
            "recommended_action": lsi_res.get("recommended_action"),
            "extracted_questions": questions
        }
        node_id = neo4j_client.create_signal_node(temp_card)
        print(f"Step 9: neo4j_client.create_signal_node - {time.time() - t0:.3f}s")
        
        # 10. Call triage_card.build_triage_card(...)
        t0 = time.time()
        upload_meta = {
            "exam_name": exam_name,
            "exam_date": exam_date,
            "source_platform": source_platform
        }
        final_card = triage_card.build_triage_card(
            signal_id=signal_id,
            upload_meta=upload_meta,
            ocr_result=raw_text,
            language_result=language_result,
            questions=questions,
            classification=classification_res,
            lsi_result=lsi_res,
            neo4j_node_id=node_id
        )
        print(f"Step 10: triage_card.build_triage_card - {time.time() - t0:.3f}s")
        
        # 12. Return triage card dict as JSONResponse with status 200
        return JSONResponse(status_code=200, content=final_card)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Pipeline failed", "detail": str(e)}
        )
    finally:
        # 11. Delete tmp file
        t0 = time.time()
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"Step 11: Delete tmp file - {time.time() - t0:.3f}s")
        except Exception:
            pass
        print(f"Total Pipeline Time: {time.time() - start_total:.3f}s")
