from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.user import User
from app.models.group_trips import GroupTrip, TripMember

with Session(engine) as db:
    mock_user = User(
        id="11111111-1111-1111-1111-111111111111",
        email="test@example.com",
        full_name="Tester",
        google_id="mock_g_id",
        avatar_url="https://ui.shadcn.com/avatars/02.png"
    )
    db.add(mock_user)
    db.commit()

    trip = GroupTrip(
        title="Sylhet Adventure Test",
        destination="Sylhet",
        start_date="2026-05-01",
        end_date="2026-05-05",
        description="Testing Feature 2",
        created_by_id=mock_user.id
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    member = TripMember(
        trip_id=trip.id,
        user_id=mock_user.id,
        role="admin"
    )
    db.add(member)
    db.commit()
    
    print("Seed Complete. Trip ID:", trip.id)
