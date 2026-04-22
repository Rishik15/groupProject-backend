from app.services import run_query
from app.services.media_storage import save_exercise_video

def create_exercise(coach_id, exercise_name, equipment, description=None, video_file=None):

    existing = run_query(
        "SELECT exercise_id FROM exercise WHERE exercise_name = :name",
        {"name": exercise_name},
        fetch=True, commit=False
    )

    if existing:
        raise ValueError(f"An exercise named '{exercise_name}' already exists")

    video_url = None
    if video_file and video_file.filename:
        result = save_exercise_video(
            coach_id=coach_id,
            uploaded_file=video_file
        )
        video_url = result["video_url"]

    run_query(
        """
        INSERT INTO exercise (exercise_name, equipment, description, video_url, created_by)
        VALUES (:exercise_name, :equipment, :description, :video_url, :created_by)
        """,
        {
            "exercise_name": exercise_name,
            "equipment": equipment,
            "description": description,
            "video_url": video_url,
            "created_by": coach_id
        },
        fetch=False, commit=True
    )

    result = run_query(
        """
        SELECT 
            exercise_id, 
            exercise_name, 
            equipment, 
            description, 
            video_url, 
            created_by 
        FROM exercise 
        WHERE exercise_name = :name
        """,
        {"name": exercise_name},
        fetch=True, commit=False
    )
    
    return result[0]