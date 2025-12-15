from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_me")

conn_str = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server={os.environ.get('DB_SERVER','localhost')},1433;"
    f"Database={os.environ.get('DB_NAME','LibraryDB')};"
    f"UID={os.environ.get('DB_USER','sa')};"
    f"PWD={os.environ.get('DB_PASS','dred.77882077')};"
    "TrustServerCertificate=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)

@app.route('/')
def book_list():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # select_pr with @book_id=0 — return all books: modify stored proc if necessary.
        cursor.execute("EXEC dbo.select_pr @book_id=?", 0)
        rows = cursor.fetchall()
        # Map rows to simple objects/dicts expected by templates.
        books = []
        seen = set()
        for r in rows:
            # r columns: book_id, title, author, year, ChapterNumber, ChapterTitle
            book_id = getattr(r, 'book_id', None) or r[0]
            if book_id in seen:
                continue
            seen.add(book_id)
            title = getattr(r, 'title', None) or r[1]
            author = getattr(r, 'author', None) or r[2]
            year = getattr(r, 'year', None) or r[3]
            books.append({
                'BookId': book_id,
                'Title': title,
                'Author': author,
                'Year': year
            })
    except Exception as e:
        flash("Error loading books.")
        books = []
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass
    return render_template('book_list.html', books=books)

@app.route('/book/<int:book_id>')
def book_card(book_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC dbo.select_pr @book_id=?", book_id)
        rows = cursor.fetchall()
        if not rows:
            flash("Book not found.")
            return redirect(url_for('book_list'))
        # First row has book metadata; contents is XML stored in table — select_pr returns chapter rows.
        r0 = rows[0]
        book = {
            'BookId': getattr(r0, 'book_id', r0[0]),
            'Title': getattr(r0, 'title', r0[1]),
            'Author': getattr(r0, 'author', r0[2]),
            'Year': getattr(r0, 'year', r0[3]),
            # We'll reconstruct contents as simple HTML list of chapters
            'Content': ''
        }
        chapters = []
        for r in rows:
            chap_title = getattr(r, 'ChapterTitle', None) or r[5]
            chap_num = getattr(r, 'ChapterNumber', None) or r[4]
            chapters.append(f"<h5>Chapter {chap_num}</h5><p>{chap_title}</p>")
        book['Content'] = "<div>" + "".join(chapters) + "</div>"
    except Exception as e:
        flash("Error loading book.")
        return redirect(url_for('book_list'))
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass
    return render_template('book_card.html', book=book)

@app.route('/add', methods=['GET', 'POST'])
def book_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        year = request.form.get('year', '').strip()
        content = request.form.get('content', '').strip()
        try:
            year_int = int(year)
        except:
            flash("Year must be a number.")
            return render_template('book_add.html')
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Stored proc expects @contents as xml — pass string; pyodbc will send as NVARCHAR, SQL will cast.
            cursor.execute("EXEC dbo.insert_pr @title=?, @author=?, @year=?, @contents=?",
                           title, author, year_int, content)
            conn.commit()
            flash("Book added.")
            return redirect(url_for('book_list'))
        except Exception as e:
            flash("Error adding book.")
        finally:
            try:
                if cursor: cursor.close()
                if conn: conn.close()
            except:
                pass
    return render_template('book_add.html')

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def book_edit(book_id):
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        year = request.form.get('year', '').strip()
        content = request.form.get('content', '').strip()
        try:
            year_int = int(year)
        except:
            flash("Year must be a number.")
            return redirect(url_for('book_edit', book_id=book_id))
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("EXEC dbo.update_pr @book_id=?, @title=?, @author=?, @year=?, @contents=?",
                           book_id, title, author, year_int, content)
            conn.commit()
            flash("Book updated.")
            return redirect(url_for('book_list'))
        except Exception as e:
            flash("Error updating book.")
        finally:
            try:
                if cursor: cursor.close()
                if conn: conn.close()
            except:
                pass
    # GET: load existing book. We'll call select_pr and reconstruct a contents XML string if possible.
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC dbo.select_pr @book_id=?", book_id)
        rows = cursor.fetchall()
        if not rows:
            flash("Book not found.")
            return redirect(url_for('book_list'))
        r0 = rows[0]
        # For editing, we prefer the raw XML contents from the table. select_pr doesn't return raw XML.
        # As workaround, query directly the table to get contents column.
        cursor.execute("SELECT contents FROM dbo.books WHERE book_id = ?", book_id)
        contents_row = cursor.fetchone()
        contents_xml = contents_row[0] if contents_row else ''
        book = {
            'BookId': getattr(r0, 'book_id', r0[0]),
            'Title': getattr(r0, 'title', r0[1]),
            'Author': getattr(r0, 'author', r0[2]),
            'Year': getattr(r0, 'year', r0[3]),
            'Content': contents_xml
        }
    except Exception as e:
        flash("Error loading book for edit.")
        return redirect(url_for('book_list'))
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass
    return render_template('book_edit.html', book=book)

@app.route('/delete/<int:book_id>', methods=['POST'])
def book_delete(book_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC dbo.delete_pr @book_id=?", book_id)
        conn.commit()
        flash("Book deleted.")
    except Exception as e:
        flash("Error deleting book.")
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass
    return redirect(url_for('book_list'))

if __name__ == '__main__':
    app.run(debug=True)
