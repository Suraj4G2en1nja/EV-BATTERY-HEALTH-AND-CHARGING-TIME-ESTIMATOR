from flask import Flask, render_template, request, session
import pandas as pd
import pickle

app = Flask(__name__)
app.secret_key = "your_secret_key"  # REQUIRED for session

# Load models
degradation_model = pickle.load(open('degradation_model.pkl', 'rb'))
charging_model = pickle.load(open('charging_time_model.pkl', 'rb'))


@app.route('/')
def index():
    return render_template(
        'index.html',
        result_degradation=session.get('result_degradation'),
        result_charging=session.get('result_charging'),
        form_data_degradation=session.get('form_data_degradation'),
        form_data_charging=session.get('form_data_charging')
    )


@app.route('/predict_degradation', methods=['POST'])
def predict_degradation():
    try:
        soc = float(request.form['soc'])
        current = float(request.form['current'])
        voltage = float(request.form['voltage'])
        battery_temp = float(request.form['battery temp'])
        ambient_temp = float(request.form['ambient temp'])
        charging_cycles = int(request.form['charging cycles'])
        battery_type_encoded = int(request.form['battery type encoded'])

        if soc < 0 or current < 0 or voltage < 0 or battery_temp < 0 or ambient_temp < 0 or charging_cycles < 0:
            raise ValueError("All values must be non-negative.")

        input_data = pd.DataFrame(
            [[soc, current, voltage, battery_temp, ambient_temp, charging_cycles, battery_type_encoded]],
            columns=['soc', 'current', 'voltage', 'battery temp', 'ambient temp',
                     'charging cycles', 'battery type encoded']
        )

        prediction = degradation_model.predict(input_data)[0]
        result = f"Degradation Rate: {round(prediction, 2)} %"

        # STORE in session
        session['result_degradation'] = result
        session['form_data_degradation'] = request.form.to_dict()

        return index()

    except Exception as e:
        session['result_degradation'] = f"Error: {str(e)}"
        return index()


@app.route('/predict_charging', methods=['POST'])
def predict_charging():
    try:
        soc = float(request.form['soc'])
        voltage = float(request.form['voltage'])
        current = float(request.form['current'])
        battery_temp = float(request.form['battery temp'])
        ambient_temp = float(request.form['ambient temp'])
        battery_type = int(request.form['battery type'])
        degradation_rate = float(request.form['degradation rate'])

        if soc < 0 or current < 0 or voltage < 0 or battery_temp < 0 or ambient_temp < 0 or degradation_rate < 0:
            raise ValueError("All values must be non-negative.")

        input_data = pd.DataFrame(
            [[soc, voltage, current, battery_temp, ambient_temp, battery_type, degradation_rate]],
            columns=['soc', 'voltage', 'current', 'battery temp', 'ambient temp',
                     'battery type', 'degradation rate']
        )

        prediction = charging_model.predict(input_data)[0]
        result = f"Charging Time: {round(prediction, 2)} hours"

        # STORE in session
        session['result_charging'] = result
        session['form_data_charging'] = request.form.to_dict()

        return index()

    except Exception as e:
        session['result_charging'] = f"Error: {str(e)}"
        return index()


@app.route('/clear')
def clear():
    session.clear()
    return index()


if __name__ == '__main__':
    app.run(debug=True)
