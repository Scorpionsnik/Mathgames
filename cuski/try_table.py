import sys
import os
import sqlite3

def make_table_uchitelya():
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS uchitelya (
		id INTEGER PRIMARY KEY,
		name TEXT,
		parol INTEGER,
		chislo_classov INTEGER,
		class0 TEXT)''')
	conn.commit()
	conn.close()

def make_table_uchenik():
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS ucheniki (
		id INTEGER PRIMARY KEY,
		name TEXT,
		parol INTEGER,
		nikname TEXT,
		posl_oc INTEGER,
		rezh INTEGER)''')
	conn.commit()
	conn.close()

def check_table_exists(table_name):
	try:
		conn = sqlite3.connect('vse.db')
		cursor = conn.cursor()
		
		# Способ 1: Через sqlite_master
		cursor.execute("""
		    SELECT name FROM sqlite_master 
		    WHERE type='table' AND name=?
		""", (table_name,))
		
		result = cursor.fetchone()
		conn.close()
		return result is not None
	    
	except sqlite3.Error:
		return False

def make_table_class(class_name):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute(f'''CREATE TABLE IF NOT EXISTS {class_name} (
		id_v_classe INTEGER PRIMARY KEY,
		id_uchenika INTEGER,
		name TEXT,
		ocenka0 INTEGER)''')
	conn.commit()
	conn.close()

def find_id(tabl_name, id1):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {tabl_name} WHERE id = ?", (id1,))
	user = cursor.fetchone()
	conn.close()
	if user:
		return user
	else:
		print(str("no user with id: "+str(id1)))

def add_uchenik(name1, parol1, posl_oc1, rezh1):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO ucheniki (name, parol, posl_oc, rezh) VALUES (?, ?, ?, ?)", (name1, parol1, posl_oc1, rezh1))
	conn.commit()
	conn.close()

def inp_dannie_uchenika():
	print("vvedi imya ychenika")
	name = input()
	print("vvedi nik ychenika")
	nikname = input()
	print("vvedi poslednuu ocenku ychenika")
	try:
		ocenka = int(input())
		if (ocenka <= 5) and (ocenka >= 1):
			pass
		else:
			print("nevozmozhnaya ocenka")
			return
	except:
		print("ne chislo")
		return
	add_uchenik(name, nikname, ocenka, 1)

def vibor_id():
	print("enter uchenik finding id:")
	try:
		idd = int(input())
	except:
		print("ne chislo")
		return
	dannie_user = find_id('ucheniki' ,idd)
	return dannie_user

def add_uchenik_to_class():
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()  
	try:
		user_id = int(input("enter user id:"))
	except:
		conn.close()
		return  
	user = find_id('ucheniki', user_id)
	if not user:
		print("User not found")
		conn.close()
		return
	print(str("we find user : " + str(user)))
	
	# ПРАВИЛЬНАЯ РАСПАКОВКА - 6 полей
	user_id, user_name, user_parol, user_nikname, user_ocenka, user_rezh = user
	
	class_name = input("enter class name: ")
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (class_name,))
	if not cursor.fetchone():
		print(f"Таблица {class_name} не существует")
		return
	cursor.execute(f"INSERT INTO {class_name} (id_v_classe, id_uchenika, name, ocenka0) VALUES (NULL, ?, ?, ?)", 
				(user_id, user_name, user_ocenka))
	print("uchenik dobavlen")
	conn.commit()
	conn.close()

def add_ocenka(class_name, id_uchenika, ocenka, nomer_ocenki):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute(f"PRAGMA table_info({class_name})")
	columns = cursor.fetchall()
	num_columns = len(columns)
	print(num_columns-3)
	if(nomer_ocenki > (num_columns - 3)):
			
		for i in range((num_columns - 3), nomer_ocenki + 1):
			ocenka_column = str("ocenka" + str(i))
			cursor.execute(f"ALTER TABLE {class_name} ADD COLUMN {ocenka_column} INTEGER")
	# cursor.execute(f"ALTER TABLE {class_name} ADD COLUMN {ocenka_column} INTEGER")
	ocenka_column_name = f"ocenka{nomer_ocenki}"
	cursor.execute(f"UPDATE {class_name} SET {ocenka_column_name} = ? WHERE id_uchenika = ?", (ocenka, id_uchenika))
	print(f"ocenka {ocenka} dobavlena ucheniku s id {id_uchenika}")
	conn.commit()
	conn.close()

def add_ocenka_requests(class_name, id_uchenika, ocenka, nomer_ocenki):
	dannie_uchenika = find_id('ucheniki', id_uchenika)
	if not dannie_uchenika:
		print("Uchenik ne naiden")
		sys.exit()
	print(dannie_uchenika)
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute("""
		SELECT name FROM sqlite_master
		WHERE type='table' AND name = ?
		""", (class_name,))
	result = cursor.fetchone()
	if not result:
		print("class ne naiden")
		conn.close()
		sys.exit()

	cursor.execute(f"SELECT * FROM {class_name} WHERE id_uchenika = ?", (id_uchenika,))
	if not cursor.fetchone():
		print("Uchenik ne v etom klasse")
		conn.close()
		sys.exit()
	print("class naiden")
		
	conn.close()
	add_ocenka(class_name, id_uchenika, ocenka, nomer_ocenki)


def dannie_dlya_dobavl_ocenki():
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	try:
		id_uchenika = int(input("vvedi id uchenika: "))
	except:
		print("ne chislo!")
		conn.close()
		return

	dannie_uchenika = find_id('ucheniki', id_uchenika)
	if not dannie_uchenika:
		print("Uchenik ne naiden")
		conn.close()
		return

	print(dannie_uchenika)
	class_uchenika = input("vvedi class uchenika: ")
	
	cursor.execute("""
		SELECT name FROM sqlite_master
		WHERE type='table' AND name = ?
		""", (class_uchenika,))
	result = cursor.fetchone()
	if not result:
		print("class ne naiden")
		conn.close()
		return

	cursor.execute(f"SELECT * FROM {class_uchenika} WHERE id_uchenika = ?", (id_uchenika,))
	if not cursor.fetchone():
		print("Uchenik ne v etom klasse")
		conn.close()
		return

	print("class naiden")

	try:
		num_ocenki = int(input("vvedii nomer octnki: "))
		if num_ocenki < 0:
			print("Nomer ocenki dolzhen byt >= 0")
			conn.close()
			return
	except:
		print("ne chislo")
		conn.close()
		return

	try:
		ocenka = int(input("vvedi ocenku: "))
		if ocenka < 1 or ocenka > 5:
			print("Ocenka dolzhna byt ot 1 do 5")
			conn.close()
			return
	except:
		print("ne chislo")
		conn.close()
		return
		
	conn.close()
	add_ocenka(class_uchenika, id_uchenika, ocenka, num_ocenki)

def parametr_dlya_classa():
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	name_class = input("enter new class name:")
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name_class,)); table_exists = cursor.fetchone() is not None
	if table_exists:
		print("est takoy class")
		return
	make_table_class(name_class)
	conn.commit()
	conn.close()

def opred_rezh(rezhim):
	if not os.path.exists('vse.db'):
		print("no table, i will make a table")
		make_table_uchenik()
	
	if rezhim == 1:
		inp_dannie_uchenika()
	elif rezhim == 2:
		uch = vibor_id()
		print(uch)
	elif rezhim == 3:
		parametr_dlya_classa()
	elif rezhim == 4:
		dannie_dlya_dobavl_ocenki()
	elif rezhim == 5:
		add_uchenik_to_class()
	else:
		print("Invalid choice")

def check_database_exists(db_name):
	"""Проверяет существует ли файл базы данных"""
	return os.path.exists(db_name)

def read_user_parol(table):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	id1 = 1
	cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id1,))
	admin_parol = cursor.fetchone()
	conn.commit()
	conn.close()
	if not admin_parol:
		print("error: ne mogu opredelit parol admina")
		mamain_menu()
	else:
		return admin_parol

def read_uchitel_parol(name):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM uchitelya WHERE name = ?", (name,))
	uchitel_data = cursor.fetchone()
	conn.close()
	if not uchitel_data:
		print("error: ne mogu opredelit parol uchitelya")
		mamain_menu()
	else:
		return uchitel_data

def read_uchenik_parol(name):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM ucheniki WHERE name = ?", (name,))
	uchitel_data = cursor.fetchone()
	conn.close()
	if not uchitel_data:
		print("error: ne mogu opredelit parol ucheniki")
		mamain_menu()
	else:
		return uchitel_data

def sozd_admin_table():
	try:
		par = int(input("vvedi celochislenniy parol dlya admina: "))
	except:
		print("ne chislo")
		return
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
		id INTEGER PRIMARY KEY,
		parol INTEGER)''')
	cursor.execute("INSERT INTO admin (parol) VALUES (?)", (par,))
	print("admin table has created")
	conn.commit()
	conn.close()

def add_uchitel(name1, parol1):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO uchitelya (name, parol) VALUES (?, ?)", (name1, parol1))
	conn.commit()
	conn.close()

def update_table_value(table_name, column_name, new_value, id_uchenika):
	"""
	Изменяет одно значение в таблице для конкретного ученика
	"""
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	
	try:
		cursor.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE id = ?", 
		              (new_value, id_value))
		conn.commit()
		print(f"Успешно обновлено: {table_name}.{column_name} = {new_value} для ID {id_value}")
	except Exception as e:
		print(f"Ошибка: {e}")
	finally:
		conn.close()

def update_uchitel_class_count(uchitel_name, new_count):
	"""Обновляет количество классов у учителя"""
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	
	try:
		cursor.execute("UPDATE uchitelya SET chislo_classov = ? WHERE name = ?", 
		              (new_count, uchitel_name))
		conn.commit()
		print(f"У учителя {uchitel_name} обновлено количество классов: {new_count}")
	except Exception as e:
		print(f"Ошибка: {e}")
	finally:
		conn.close()

def delete_by_name(table_name, name_value):
	"""Удалить строку по имени"""
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute(f"DELETE FROM {table_name} WHERE name = ?", (name_value,))
	conn.commit()
	
	if cursor.rowcount > 0:
		print(f"Удалена строка с именем '{name_value}' из таблицы {table_name}")
	else:
		print(f"Строка с именем '{name_value}' не найдена")
	
	conn.close()

def find_by_name(tabl_name, name):
	conn = sqlite3.connect('vse.db')
	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {tabl_name} WHERE name = ?", (name,))
	user = cursor.fetchone()
	conn.close()
	return user

def vhod_admin():
	try:
		parol = int(input("vvedi parol admina:"))
	except:
		print("ne chislo")
		return

	admin_data = read_user_parol('admin')


	if admin_data and parol == admin_data[1]:
		print("viberi deystvie: 1 - sozdat uchitelya; 2 - ydalit uchitelya")
		try:
			rezhim = int(input("vvedi svoi vibor: "))
		except:
			print("ne chislo")
			return
		if rezhim == 1:
			if not check_table_exists('uchitelya'):
				print("no table for uchetelya we will make it")
				make_table_uchitelya()
			else:
				new_uch_name = input("vvedi imya uchitelya: ")
				try:
					parol_uch = int(input("vvedi celochislenniy parol dlya uchitelya: "))
				except:
					print("ne chislo")
					return
				add_uchitel(new_uch_name, parol_uch)
		elif rezhim == 2:
			if not check_table_exists('uchitelya'):
				print("no table for uchetelya we will make it")
				make_table_uchitelya()
			else:
				name_del_uchitelya = input("vvedi imya udalyaemogo uchitelya: ")
				delete_by_name('uchitelya', name_del_uchitelya)
		else:
			print("invalid number")
			return
	else:
		print("neverniy parol")

def vhod_uchitel():
	uchitel = input("vvedite imya uchitelya: ")
	sush_uchitel = find_by_name('uchitelya', uchitel)
	if not sush_uchitel:
		print("net takogo uchitelya")
		return
	try:
		parol = int(input("vvedi parol uchitelya:"))
	except:
		print("ne chislo")
		return

	uchitel_parol = read_uchitel_parol(uchitel)


	if uchitel_parol and parol == uchitel_parol[2]:
		print("viberi deystvie: 1 - sozdat uchenika; 2 - ydalit uchenika; 3 - sozdat class ; 4 - dobavit uchenika v class; 5 - naiti uchenika po id; 6 - naiti class; 7 - dobavit ucheniku ocenku")
		try:
			rezhim = int(input("vvedi svoi vibor: "))
		except:
			print("ne chislo")
			return
		if rezhim == 1:
			if not check_table_exists('ucheniki'):
				print("no table for ucheniki we will make it")
				make_table_uchenik()
			else:
				new_uch_name = input("vvedi imya uchenika: ")
				try:
					parol_uch = int(input("vvedi celochislenniy parol dlya uchenika: "))
				except:
					print("ne chislo")
					return
				try:
					posl_oc = int(input("vvedi poslednuu ocenku uchenika: "))
					if ((posl_oc < 6) and (posl_oc > 1)):
						pass
					else:
						print("nevozmozhnaya ocenka")
						return
				except:
					print("ne chislo")
					return
				add_uchenik(new_uch_name, parol_uch, posl_oc, 1)
		elif rezhim == 2:
			if not check_table_exists('ucheniki'):
				print("no table for uchetelya we will make it")
				make_table_uchenik()
			else:
				name_del_uchenika = input("vvedi imya udalyaemogo uchenika: ")
				delete_by_name('ucheniki', name_del_uchenika)
		elif rezhim == 3:
			new_class_name = input("vvedi nazvanie novogo classa: ")
			if check_table_exists(new_class_name):
				print("takoi class yzhe est")
				return
			
			# Получаем текущие данные учителя
			current_count = uchitel_parol[3] if uchitel_parol[3] is not None else 0
			new_count = current_count + 1
			
			# Создаем таблицу класса
			make_table_class(new_class_name)
			
			# Обновляем количество классов у учителя
			update_uchitel_class_count(uchitel, new_count)  # используем переменную uchitel вместо uchitel_name
			
			# Если это первый класс, сохраняем его название в class0
			if new_count == 1:
				conn = sqlite3.connect('vse.db')
				cursor = conn.cursor()
				cursor.execute("UPDATE uchitelya SET class0 = ? WHERE name = ?", 
							(new_class_name, uchitel))
				conn.commit()
				conn.close()

			else:
				# new_count = new_count - 1
				conn = sqlite3.connect('vse.db')
				cursor = conn.cursor()

				cursor.execute("PRAGMA table_info(uchitelya)")
				columns = cursor.fetchall()

				class_columns = [col[1] for col in columns if col[1].startswith('class')]
				num_class_columns = len(class_columns)

				new_class_column = f"class{num_class_columns}"

				cursor.execute(f"ALTER TABLE uchitelya ADD COLUMN {new_class_column} TEXT")
				cursor.execute(f"UPDATE uchitelya SET {new_class_column} = ? WHERE name = ?", 
							(new_class_name, uchitel))
				conn.commit()
				conn.close()
			print(f"Class {new_class_name} sozdan i dobavlen uchitelyu {uchitel}")
		elif rezhim == 4:
			if not check_table_exists('ucheniki'):
				print("no table for uchetelya we will make it")
				make_table_uchenik()
			else:
				add_uchenik_to_class()

		elif rezhim == 5:
			if not check_table_exists('ucheniki'):
				print("no table for uchetelya we will make it")
				make_table_uchenik()
			else:
				dannie = vibor_id()
				print(dannie)

		elif rezhim == 6:
			print("dannaya funkciya poka ne dostupna")
			return

		elif rezhim == 7:
			if not check_table_exists('ucheniki'):
				print("no table for uchetelya we will make it")
				make_table_uchenik()
			else:
				dannie_dlya_dobavl_ocenki()

		else:
			print("invalid number")
			return
	else:
		print("neverniy parol")

def vhod_uchenik():
	uchenik = input("vvedite imya uchenika: ")
	sush_uchenik = find_by_name('ucheniki', uchenik)
	if not sush_uchenik:
		print("net takogo uchenika")
		return
	try:
		parol = int(input("vvedi parol uchenika:"))
	except:
		print("ne chislo")
		return

	uchitel_parol = read_uchenik_parol(uchenik)
	# uchitel_parol = read_uchitel_parol(uchitel)


	if uchitel_parol and parol == uchitel_parol[2]:
		print("viberi deystvie: 1 - poluchit ocenku")
		try:
			rezhim = int(input("vvedi svoi vibor: "))
		except:
			print("ne chislo")
			return
		if rezhim == 1:
			class_uchenika = input("enter your class name: ")
			conn = sqlite3.connect('vse.db')
			cursor = conn.cursor()

			cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (class_uchenika,))
			if not cursor.fetchone():
				print(f"Таблица {class_uchenika} не существует")
				conn.close()
				return
			try:
				ocenka = int(input("vvedi ocenku: "))
				if ((ocenka > 5) or (ocenka < 2)):
					print("nevozmoznaya ocenka")
					conn.close()
					return

				cursor.execute(f"PRAGMA table_info({class_uchenika})")
				columns = cursor.fetchall()
				num_columns = len(columns)
				num_columns = num_columns-3
				conn.close()
				add_ocenka(class_uchenika, uchitel_parol[0], ocenka, num_columns)
			except:
				print("ne chislo")
				conn.close()
				return
		else:
			print("invalid number")
			return
	else:
		print("neverniy parol")

def opred_vhoda(rezhim):
	if check_database_exists('vse.db'):
		if rezhim == 1:
			if check_table_exists('admin'):
				vhod_admin()
			else:
				print("no admin table")
				sozd_admin_table()
		elif rezhim == 2:
			if check_table_exists('uchitelya'):
				vhod_uchitel()
			else:
				print("no teacher table, ask admin to make it")
				return
		elif rezhim == 3:
			vhod_uchenik()
			# if check_table_exists('ucheniki'):
		else:
			print("invalid number")
			return
	else:
		sozd_admin_table()
		return

def main_menu():
	print("1 sozdat uchenika, 2 naiti uchenika po id, 3 sozdat class, 4 dobavit ocenku, 5 add uchen v class: choose")
	try: 
		vibor_polzovatelya = int(input(" "))
		opred_rezh(vibor_polzovatelya)
	except:
		print("it is not integer")

def mamain_menu():
	print("1 - voiti admin; 2 - voiti uchitel; 3 - voiti uchenik")
	try:
		vibor_usera = int(input(" :"))
		opred_vhoda(vibor_usera)
	except:
		print("ne chislo")

# mamain_menu()