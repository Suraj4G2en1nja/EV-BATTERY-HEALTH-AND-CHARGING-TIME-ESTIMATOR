from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

# Load models
degradation_model = pickle.load(open('degradation_model.pkl', 'rb'))
charging_model = pickle.load(open('charging_time_model.pkl', 'rb'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict_degradation', methods=['POST'])
def predict_degradation():
    try:
        # Extract data from form
        soc = float(request.form['soc'])
        current = float(request.form['current'])
        voltage = float(request.form['voltage'])
        battery_temp = float(request.form['battery temp'])
        ambient_temp = float(request.form['ambient temp'])
        charging_cycles = int(request.form['charging cycles'])
        battery_type_encoded = int(request.form['battery type encoded'])

        # Ensure no negative values are passed
        if soc < 0 or current < 0 or voltage < 0 or battery_temp < 0 or ambient_temp < 0 or charging_cycles < 0:
            raise ValueError("All values must be non-negative.")

        input_data = pd.DataFrame(
            [[soc, current, voltage, battery_temp, ambient_temp, charging_cycles, battery_type_encoded]],
            columns=['soc', 'current', 'voltage', 'battery temp', 'ambient temp',
                     'charging cycles', 'battery type encoded'])

        prediction = degradation_model.predict(input_data)[0]
        result = f" Degradation Rate: {round(prediction, 2)} %"

        # Pass form data and result back to the template
        return render_template('index.html', result_degradation=result, form_data_degradation=request.form)

    except Exception as e:
        return render_template('index.html', result_degradation=f"Error: {str(e)}", form_data_degradation=request.form)


@app.route('/predict_charging', methods=['POST'])
def predict_charging():
    try:
        # Extract data from form
        soc = float(request.form['soc'])
        voltage = float(request.form['voltage'])
        current = float(request.form['current'])
        battery_temp = float(request.form['battery temp'])
        ambient_temp = float(request.form['ambient temp'])
        battery_type = int(request.form['battery type'])
        degradation_rate = float(request.form['degradation rate'])

        # Ensure no negative values are passed
        if soc < 0 or current < 0 or voltage < 0 or battery_temp < 0 or ambient_temp < 0 or degradation_rate < 0:
            raise ValueError("All values must be non-negative.")

        input_data = pd.DataFrame([[soc, voltage, current, battery_temp, ambient_temp, battery_type, degradation_rate]],
                                  columns=['soc', 'voltage', 'current', 'battery temp', 'ambient temp', 'battery type',
                                           'degradation rate'])

        prediction = charging_model.predict(input_data)[0]
        result = f" Charging Time: {round(prediction, 2)} hours"

        # Pass form data and result back to the template
        return render_template('index.html', result_charging=result, form_data_charging=request.form)

    except Exception as e:
        return render_template('index.html', result_charging=f"Error: {str(e)}", form_data_charging=request.form)


if __name__ == '__main__':
    app.run(debug=True)
