from fastapi import HTTPException, Request


def get_detector(req: Request):
    detector = getattr(req.state, "detector", None) or getattr(
        req.app.state, "detector", None
    )
    if detector is None:
        raise HTTPException(
            status_code=503, detail="Detector service is not available right now."
        )
    return detector


def get_fact_checker(req: Request):
    fact_checker = getattr(req.state, "fact_checker", None) or getattr(
        req.app.state, "fact_checker", None
    )
    if fact_checker is None:
        raise HTTPException(
            status_code=503, detail="Fact checker service is not available right now."
        )
    return fact_checker
