from aiven_db_connect import connect_to_aiven

def update_procedure():
    """
    Update the getSectionSchedule procedure to match the expected column count
    """
    connection, cursor = connect_to_aiven()
    
    if connection and cursor:
        try:
            # Drop existing procedure
            cursor.execute('DROP PROCEDURE IF EXISTS getSectionSchedule')
            
            # Create new procedure with exactly three columns
            create_proc = """
            CREATE PROCEDURE getSectionSchedule(IN section_id INT)
            BEGIN
                SELECT 
                    sd.day, 
                    TIME_FORMAT(st.startTime, '%H:%i') AS start_time,
                    TIME_FORMAT(st.endTime, '%H:%i') AS end_time
                FROM 
                    sectionday sd 
                    JOIN sectiontime st ON sd.sectionID = st.sectionID
                WHERE 
                    sd.sectionID = section_id
                ORDER BY 
                    FIELD(sd.day, 'Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
                    st.startTime;
            END
            """
            
            # Execute create procedure
            cursor.execute(create_proc)
            connection.commit()
            
            # Verify procedure exists
            cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'defaultdb' AND Name = 'getSectionSchedule'")
            result = cursor.fetchone()
            
            if result:
                print(f"Procedure getSectionSchedule created successfully!")
            else:
                print("Failed to create procedure.")
            
            # Show the procedure definition
            cursor.execute("SHOW CREATE PROCEDURE getSectionSchedule")
            proc_def = cursor.fetchone()
            if proc_def:
                print("\nProcedure definition:")
                print(proc_def[2])
                
        except Exception as e:
            print(f"Error updating procedure: {e}")
        finally:
            connection.close()
            print("Connection closed")
    else:
        print("Failed to connect to database")

if __name__ == "__main__":
    update_procedure() 