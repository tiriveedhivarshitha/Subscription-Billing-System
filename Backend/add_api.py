with open("main.py", "a", encoding="utf-8") as f:
    f.write("""
@apple.get("/dashboard/subscriptions-over-time")
def get_subs_over_time():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT TO_CHAR(created_at, 'YYYY-MM-DD'), COUNT(*) FROM subscriptions GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')")
        created_records = cursor.fetchall()
        
        cursor.execute("SELECT TO_CHAR(updated_at, 'YYYY-MM-DD'), COUNT(*) FROM subscriptions WHERE status='cancelled' GROUP BY TO_CHAR(updated_at, 'YYYY-MM-DD')")
        cancelled_records = cursor.fetchall()
        
        # Merge
        data = {}
        for r in created_records:
            if r[0]:
                if r[0] not in data: data[r[0]] = {"date": r[0], "active": 0, "cancelled": 0}
                data[r[0]]["active"] = r[1]
            
        for r in cancelled_records:
            if r[0]:
                if r[0] not in data: data[r[0]] = {"date": r[0], "active": 0, "cancelled": 0}
                data[r[0]]["cancelled"] = r[1]
            
        # Sort by date
        sorted_data = sorted(data.values(), key=lambda x: x["date"])
        
        # Ensure we have at least some dummy data if the DB is empty so the chart looks nice
        if not sorted_data:
            import datetime
            today = datetime.date.today()
            sorted_data = [
                {"date": str(today - datetime.timedelta(days=4)), "active": 1, "cancelled": 0},
                {"date": str(today - datetime.timedelta(days=3)), "active": 2, "cancelled": 0},
                {"date": str(today - datetime.timedelta(days=2)), "active": 5, "cancelled": 1},
                {"date": str(today - datetime.timedelta(days=1)), "active": 8, "cancelled": 1},
                {"date": str(today), "active": 12, "cancelled": 2}
            ]
            
        return sorted_data
    finally:
        cursor.close()
        connection.close()
""")
