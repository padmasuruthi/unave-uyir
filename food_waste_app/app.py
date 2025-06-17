from flask import Flask, render_template, request, redirect, session
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    phone = request.form['phone']
    password = request.form['password']
    user_type = request.form['user_type']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, phone, password, user_type) VALUES (%s, %s, %s, %s)", 
                   (name, phone, password, user_type))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    phone = request.form['phone']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['user_type'] = user['user_type']
        if user['user_type'] == 'donor':
            return redirect('/donor_dashboard')
        else:
            return redirect('/receiver_dashboard')
    else:
        return "Invalid Login"

@app.route('/donor_dashboard')
def donor_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # JOIN to get receiver name and phone if accepted
    cursor.execute("""
        SELECT d.*, u.name AS receiver_name, u.phone AS receiver_phone
        FROM donations d
        LEFT JOIN users u ON d.receiver_id = u.id
        WHERE d.donor_id = %s
    """, (user_id,))
    
    donations = cursor.fetchall()
    conn.close()
    return render_template('donor_dashboard.html', donations=donations)


@app.route('/donate')
def donate_form():
    return render_template('donate_form.html')

@app.route('/submit_donation', methods=['POST'])
def submit_donation():
    donor_id = session.get('user_id')
    food_type = request.form['food_type']
    location = request.form['location']
    expiry_time = request.form['expiry_time']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO donations (donor_id, food_type, location, expiry_time) VALUES (%s, %s, %s, %s)",
                   (donor_id, food_type, location, expiry_time))
    conn.commit()
    conn.close()
    return redirect('/donor_dashboard')

@app.route('/receiver_dashboard')
def receiver_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.*, u.name AS donor_name, u.phone AS donor_phone
        FROM donations d
        JOIN users u ON d.donor_id = u.id
    """)
    donations = cursor.fetchall()
    conn.close()

    return render_template('receiver_dashboard.html', donations=donations, user_id=user_id)



@app.route('/request_donation/<int:donation_id>')
def request_donation(donation_id):
    receiver_id = session.get('user_id')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE donations SET status = 'requested', receiver_id = %s WHERE id = %s",
                   (receiver_id, donation_id))
    conn.commit()
    conn.close()
    return redirect('/receiver_dashboard')

@app.route('/accept/<int:donation_id>', methods=['POST'])
def accept_donation(donation_id):
    receiver_id = session.get('user_id')
    if not receiver_id:
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()
    
    # Only update if currently available
    cursor.execute("""
        UPDATE donations
        SET status = 'accepted', receiver_id = %s
        WHERE id = %s AND status = 'available'
    """, (receiver_id, donation_id))
    
    conn.commit()
    conn.close()
    
    return redirect('/receiver_dashboard')

@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
