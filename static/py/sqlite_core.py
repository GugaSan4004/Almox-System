import sqlite3

from datetime import datetime

class init:
    def __init__(self, folder) -> None:
        self.conector = sqlite3.connect(folder + r"\almoxarifado.sqlite", check_same_thread=False)

    class mails:
        def __init__(self, parent: "init") -> None:
            self.connection = parent.conector
            self.connection: sqlite3.Connection = self.connection
            self.temp_orderBy = ""
            self.direction_orderBy = ""
            
        def updatePicture(self, receive_name, receive_date, photo_id, code):
            cur = self.connection.cursor()
            cur.execute(
                "UPDATE mails SET receive_name = ?, receive_date = ?, photo_id = ?, status = 'shipped' WHERE code = ?",
                (receive_name, receive_date, photo_id, code.upper())
            )
            self.connection.commit()
            
            cur.close()

        def updateReceiver(self, code, receiver, sender):
            cur = self.connection.cursor()
            try:
                cur.execute(
                    "UPDATE mails SET ReceivedOnReceptionBy = ?, SendedOnReceptionBy = ?, status = 'almox' WHERE code = ?",
                    (receiver, sender, code.upper())
                )
                self.connection.commit()
            except Exception as e:
                print(e)
            
            cur.close()
            
        def register(self, name: str, code: str, fantasy: str, type_: str, priority: str, status: str):
            cur = self.connection.cursor()
            try:
                cur.execute("""
                    INSERT INTO mails (name, code, fantasy, type, priority, status, join_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                        name.title(), 
                        code.upper(), 
                        fantasy.title(), 
                        type_.title(), 
                        priority.title(),
                        status,
                        datetime.now().strftime("%d-%m-%Y")
                    )
                )
                self.connection.commit()
            except Exception as e:
                return e
            cur.close()
        
        def getMails(self, filter, orderBy):
            cur = self.connection.cursor()
            
            if filter:   
                if orderBy == self.temp_orderBy:
                    self.direction_orderBy = "DESC" if self.direction_orderBy == "ASC" else "ASC"
                else:
                    self.temp_orderBy = orderBy
                    self.direction_orderBy = "DESC"
                    
                cur.execute(
                    f"SELECT * FROM mails WHERE code LIKE ? OR name LIKE ? OR fantasy LIKE ? OR photo_id LIKE ? ORDER BY {orderBy}  {self.direction_orderBy}",
                    (
                        "%" + filter + "%", 
                        "%" + filter + "%", 
                        "%" + filter + "%",
                       "%" + filter + "%"
                    )
                )
                correspondences = cur.fetchmany(200)
            else:
                
                if orderBy == self.temp_orderBy:
                    self.direction_orderBy = "DESC" if self.direction_orderBy == "ASC" else "ASC"
                else:
                    self.temp_orderBy = orderBy
                    self.direction_orderBy = "DESC"
                
                cur.execute(f"SELECT * FROM mails ORDER BY {orderBy} {self.direction_orderBy}")
                
                correspondences = cur.fetchmany(200)
                
            cur.close()

            return correspondences
        
    class tools:
        def __init__(self, parent: "init") -> None:
            self.connection = parent.conector
        
        def getMovementsCount(self):
            cur = self.connection.cursor()
            cur.execute("SELECT MAX(id) FROM tools_movements")
            
            count: int = cur.fetchone()[0]
            
            cur.close()
            return 1 if count is None else count + 1
        
        def setToolMissing(self, code: str):
            cur = self.connection.cursor()
            cur.execute("UPDATE tools set id_movements = NULL WHERE (id = ? OR nome LIKE ?)", 
                (code, "%" + code + "%")
            )
            
            self.connection.commit()
            
            cur.close()
        
        def searchTools(self, code: str):
            cur = self.connection.cursor()
            
            if not code:
                cur.execute("SELECT * FROM tools")
                result = cur.fetchall()
            else:
                cur.execute("SELECT * FROM tools WHERE id LIKE '%' || ? || '%' OR nome LIKE '%' || ? || '%' OR id_alternative LIKE '%' || ? || '%'", (code, code, code))
                result = cur.fetchone()

            cur.close()
            return result
        
        def updateTools(self, id, column, value) -> None:
            cur = self.connection.cursor()
            
            cur.execute(f"UPDATE tools SET {column} = ? WHERE id = ?", (value, id))
            self.connection.commit()
            
            cur.close()
        
        def addMovement(self, id, item, day, month, year, time, type):
            cur = self.connection.cursor()
            
            cur.execute("INSERT INTO tools_movements (id, item, day, month, year, time, type) VALUES (?, ?, ?, ?, ?, ?, ?)", (str(id).zfill(6), item, day, month, year, time, type))
            cur.execute("SELECT * FROM tools_movements WHERE id = ?", (str(id).zfill(6),))
            result = cur.fetchone()
            
            self.connection.commit()
            cur.close()

            return result 

        def getAllLoanedItems(self):
            cur = self.connection.cursor()
            
            cur.execute("SELECT * FROM tools WHERE status = 'Emprestado'")
            results = cur.fetchall()
            
            cur.close()
            return results

        def getAllMovements(self):
            cur = self.connection.cursor()
            
            cur.execute("SELECT * FROM tools_movements ORDER BY id DESC")
            results = cur.fetchall()
            
            cur.close()
            return results