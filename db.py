import sqlite3


def create_tables():
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS league (id INTEGER PRIMARY KEY, name TEXT, year INTEGER)"
    )
    conn.commit()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT, logo TEXT, league_id INTEGER, FOREIGN KEY(league_id) REFERENCES league(id))"
    )
    conn.commit()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, team_id INTEGER, points INTEGER, played INTEGER, goals_against INTEGER, goals_for INTEGER, wins INTEGER, draws INTEGER, losses INTEGER, position TEXT, FOREIGN KEY(team_id) REFERENCES teams(id))"
    )
    conn.commit()
    conn.close()


def insert_leagues(leagues):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    prev_leagues = [
        row[0] for row in cursor.execute("SELECT name FROM league").fetchall()
    ]
    if (leagues[0]) not in prev_leagues:
        cursor.execute(
            "INSERT INTO league (name, year) VALUES (?, ?)",
            (leagues[0], leagues[1]),
        )
    else:
        update_league = cursor.execute(
            "SELECT name, year FROM league WHERE name = ?", (leagues[0],)
        ).fetchone()
        if update_league[1] != leagues[1]:
            cursor.execute(
                "UPDATE league SET year = ? WHERE name = ?",
                (leagues[1], leagues[0]),
            )
            cursor.execute("DELETE FROM stats")
            cursor.execute("DELETE FROM teams")
    conn.commit()
    conn.close()


def insert_teams(teams):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    prev_teams = cursor.execute("SELECT name FROM teams").fetchall()
    for team_name, team_data in teams.items():
        team_data["league"] = cursor.execute(
            "SELECT id FROM league WHERE name = ?", (team_data["league"],)
        ).fetchone()[0]
        if (team_data["nombre"],) not in prev_teams:
            cursor.execute(
                "INSERT INTO teams (name, league_id, logo) VALUES (?, ?, ?)",
                (team_data["nombre"], team_data["league"], team_data["logo"]),
            )
        else:
            cursor.execute(
                "UPDATE teams SET name = ?, league_id = ?, logo = ? WHERE name = ?",
                (team_data["nombre"], team_data["league"], team_data["logo"], team_data["nombre"]),
            )
        conn.commit()
        insert_stats(team_data["estadisticas"], team_data["nombre"])
    conn.commit()
    conn.close()


def insert_stats(stat, nombreEquipo):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    team_id = cursor.execute("SELECT id FROM teams WHERE name = ?", (nombreEquipo,)).fetchone()
    team_id = team_id[0]
    prev_stats = cursor.execute("SELECT team_id FROM stats").fetchall()
    if (team_id,) in prev_stats:
        cursor.execute(
            "UPDATE stats SET position = ?, points = ?, played = ?, goals_against = ?, goals_for = ?, wins = ?, draws = ?, losses = ? WHERE team_id = ?",
            (
                stat["rank"],
                stat["points"],
                stat["gamesPlayed"],
                stat["pointsAgainst"],
                stat["pointsFor"],
                stat["wins"],
                stat["ties"],
                stat["losses"],
                team_id,
            ),
        )
    else:
        cursor.execute(
            "INSERT INTO stats (position, team_id, points, played, goals_against, goals_for, wins, draws, losses) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                stat["rank"],
                team_id,
                stat["points"],
                stat["gamesPlayed"],
                stat["pointsAgainst"],
                stat["pointsFor"],
                stat["wins"],
                stat["ties"],
                stat["losses"],
            ),
        )
    conn.commit()
    conn.close()

if __name__=="__main__":
    create_tables()
    insert_leagues(
        [{"name": "Premier League", "year": 2024}, {"name": "La Liga", "year": 2024}]
    )
    insert_teams(
        [
            {
                "name": "Manchester United",
                "league": "Premier League",
                "logo": "manu_logo.png",
            },
            {"name": "Real Madrid", "league": "La Liga", "logo": "realmadrid_logo.png"},
        ]
    )
    insert_stats(
        [
            {
                "position": "1",
                "team_id": 1,
                "points": 85,
                "played": 38,
                "goals_against": 30,
                "goals_for": 70,
                "wins": 27,
                "draws": 4,
                "losses": 7,
            },
            {
                "position": "2",
                "team_id": 2,
                "points": 83,
                "played": 38,
                "goals_against": 25,
                "goals_for": 65,
                "wins": 25,
                "draws": 5,
                "losses": 8,
            },
        ]
    )
