SCAPS : 

Energy Analysis and Forecasting Streamlit Page :

🧭 1. High-Level Purpose

This Streamlit page performs Energy Consumption Analysis and Forecasting for multiple buildings.
It helps you:

Explore and filter historical energy data

Visualize consumption trends and patterns

Analyze efficiency by building size and floors

Compare multiple machine learning models

Forecast future weekly energy consumption

⚙️ 2. Key Functional Sections
2.1 Data Loading and Preprocessing
df = get_table("energy")
df['date'] = pd.to_datetime(df['date'])
df['week_num'] = df['date'].dt.isocalendar().week


Loads energy data from your database (via get_table()).

Converts the date field to datetime format.

Extracts the ISO week number to group data weekly.

2.2 Overview and Filters
🗓️ Week Filter
selected_week = st.slider("Week Number", min_value=min_week, max_value=max_week, value=(min_week, max_week))


Lets users select a range of weeks (e.g., week 10–30).

Filters data for only those weeks.

🏢 Building Filter
selected_buildings = st.multiselect("Buildings", options=buildings, default=buildings)


Allows selecting one or more buildings.

Automatically defaults to all buildings.

2.3 Consumption Trends
Daily Energy Consumption
df_daily = df_filtered.groupby(['date','building'])['energy_kwh'].mean().reset_index()


Aggregates energy data daily.

Plots:

Actual daily energy usage

7-day moving average for smoothed trends

📊 Output:

Two interactive Plotly charts:

Daily consumption

7-day rolling average trend

🏢 3. Top 5 Buildings by Average Energy
top_buildings = df_filtered.groupby("building")["energy_kwh"].mean()...


Ranks buildings based on average energy consumption.

Displays a bar chart of top 5 energy consumers.

Helps identify energy-intensive buildings.

⚡ 4. Energy Efficiency Analysis
df_eff["energy_per_sqm_floor"] = df_eff["energy_kwh"] / (df_eff["building_area_sqm"] * df_eff["floor_count"])


Evaluates efficiency by normalizing energy against building area and number of floors.

Lower value = better efficiency.

Shown as a color-coded bar chart (green = efficient, red = inefficient).

🧩 Insight:
This helps compare buildings of different sizes fairly.

🤖 5. Model Training and Comparison
Features
features = ['temp_c','humidity_pct',...,'class_event_count']


Uses environmental, occupancy, and structural factors as predictors.

Adds lag features (previous weeks’ energy):

for lag in [1,2]:
    df_weekly[f'lag_{lag}'] = df_weekly.groupby('building')['energy_kwh'].shift(lag)

Models Compared:
Model	Description
Linear Regression	Baseline model; assumes linear relationships
Random Forest	Ensemble tree-based model for non-linear patterns
KNN Regressor	Uses nearest data points; good for localized trends
SVR (Support Vector Regression)	Works well with small data and non-linear kernels
Model Metrics:

R² Score: Measures fit quality (1.0 = perfect)

MAPE: Mean Absolute Percentage Error (lower is better)

Automatic Model Selection:
best_model_row = results_df.loc[results_df["MAPE"].idxmin()]


Chooses the lowest MAPE model as the best predictor.

Displays a comparison table.

📊 Example:

Model	R²	MAPE
Random Forest	0.92	8.3
SVR	0.85	9.1
✅ Best Model: Random Forest		
🔮 6. Forecasting Future Weeks
num_future_weeks = st.slider("Forecast Weeks Ahead", 1, 8, 2)


Allows forecasting up to 8 future weeks.

Uses the best-performing model.

Adds small noise and trend adjustment to simulate realistic fluctuations:

noise = np.random.normal(0, base_pred * 0.05)
trend_adj = i * 0.02 * base_pred

📈 7. Visualization: Actual vs Predicted

Combines:

Past actuals

Bridge point (to ensure continuity)

Future predictions

Creates a continuous time-series line chart.

Gray shaded region = forecast area.

🧩 8. Key Insights

✅ User Flexibility:

Filter by building and week range

Adjust future forecast horizon

✅ Analytics Depth:

Top consumer analysis

Energy efficiency metrics

ML model comparison and forecasting

✅ ML Automation:

Feature engineering (lag features)

Model selection based on MAPE

Forecast generation with continuity

📘 Summary for Presentation

“The Energy Analysis dashboard provides an end-to-end view of building energy consumption, efficiency, and predictive analytics.
Users can explore patterns, benchmark efficiency, and forecast future consumption using the most accurate model selected dynamically based on MAPE performance.”


Faculty Analysis Streamlit Page

Absolutely! Let’s break down your Faculty Workload Prediction Dashboard in detail, explaining how the prediction works, how overload risk is derived, and what each part of the code is doing.

1️⃣ Page Setup & Data Loading
st.set_page_config(page_title="Faculty Workload Dashboard", layout="wide")
st.title("👨‍🏫 Faculty Workload & Predicted Overload Risk Dashboard")

# Load faculty data
df = get_table("faculty")


st.set_page_config sets the dashboard title and layout.

get_table("faculty") loads the faculty data from your database.

At this stage, df contains all your columns like:

faculty_id, department, classes_handled_per_week, leaves_taken, research_projects, experience_years, publications, courses_taught, etc.

2️⃣ Workload Prediction

This is the core part where we predict workload hours for each faculty.

features = ['classes_handled_per_week','leaves_taken','research_projects','experience_years','publications','courses_taught']
target = 'workload_hours'

X = df[features]
y = df[target]


Features (X): These are the independent variables used to predict workload hours.

classes_handled_per_week → Number of classes faculty teach

leaves_taken → Days absent

research_projects → Number of research projects handled

experience_years → Faculty experience

publications → Academic publications

courses_taught → Number of courses taught

Target (y): This is what we are trying to predict → workload_hours.

Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


80% training data: used to train the model

20% test data: used to evaluate how well the model predicts unseen data

Regression Models
@st.cache_resource
def train_workload_models(X_train, y_train, X_test, y_test):
    rf = RandomForestRegressor(n_estimators=150, random_state=42)
    rf.fit(X_train, y_train)
    rf_r2 = r2_score(y_test, rf.predict(X_test))
    
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_r2 = r2_score(y_test, lr.predict(X_test))
    
    best_model = rf if rf_r2 >= lr_r2 else lr
    best_r2 = max(rf_r2, lr_r2)
    mae = mean_absolute_error(y_test, best_model.predict(X_test))
    return best_model, best_r2, mae


Random Forest Regressor (rf):

Ensemble of decision trees.

Captures non-linear relationships like “more research projects + many classes → higher workload”.

R² score is calculated to check predictive accuracy.

Linear Regression (lr):

Models linear relationship between features and workload hours.

Simple, interpretable.

Best model selection:

Whichever model has higher R² score is selected as the final workload predictor.

MAE (Mean Absolute Error) shows average prediction error in hours.

Predict Workload
df['predicted_workload_hours'] = workload_model.predict(df[features])


For each faculty, we predict workload hours using the trained model.

This column is now independent of actual workload_hours—it’s purely model-based prediction.

3️⃣ Overload Risk
OVERLOAD_THRESHOLD = 30
df['predicted_overload_risk'] = (df['predicted_workload_hours'] > OVERLOAD_THRESHOLD).astype(int)


We set a threshold (30 hours/week).

If predicted_workload_hours exceeds this threshold → overload_risk = 1 (faculty at risk).

Otherwise → overload_risk = 0 (normal workload).

✅ This creates a binary classification based on regression output, without training a separate classifier.

4️⃣ Faculty at Risk Table
overloaded_faculty = df[df['predicted_overload_risk'] == 1]
st.dataframe(overloaded_faculty[['faculty_id', 'department', 'predicted_workload_hours', ...]])


Displays faculty who are predicted to be overloaded.

Useful for administrators to quickly identify staff at risk.

5️⃣ Scatter Plot: Predicted Workload vs Classes
fig = px.scatter(
    df, 
    x="classes_handled_per_week", 
    y="predicted_workload_hours", 
    color="predicted_overload_risk",
    hover_data=['faculty_id','experience_years','research_projects','leaves_taken','publications','courses_taught'],
    title="Predicted Workload Hours by Classes Handled"
)


X-axis: Classes handled per week

Y-axis: Predicted workload hours

Color: Red = overload risk, Green = normal

Hover data: Displays extra faculty details

Adds horizontal line for overload threshold for visual reference.

✅ Helps spot trends like:

“Faculty teaching many classes and projects are at high risk.”

6️⃣ Department-wise Analytics

Shows leaves, publications, workshops, awards per department using different chart types.

Aggregation:

dept_agg = df.groupby('department').agg({
    'leaves_taken':'sum',
    'publications':'sum',
    'workshops_attended':'sum',
    'awards_received':'sum',
    'faculty_id':'count'  # total faculty per department
}).reset_index().rename(columns={'faculty_id':'faculty_count'})


Plots 4 charts side by side with hover info showing:

Metric value

Total faculty in the department

Chart types: Pie, horizontal bar, treemap, donut for variety and readability.

7️⃣ Summary of Prediction Method

Select features → classes_handled_per_week, leaves_taken, research_projects, experience_years, publications, courses_taught.

Train regression models on 80% of data: Random Forest & Linear Regression.

Evaluate on 20% test set → choose best R² model.

Predict workload hours for all faculty.

Determine overload risk using a threshold.

Visualize: Scatter plot (faculty workload vs classes) + department metrics charts.

How Overload Risk Works

This is a threshold-based classification, not a separate model.

If you want, we can also train a classifier (RandomForestClassifier) to predict overload risk directly from features, which may capture complex relationships beyond just thresholding hours.

Facility Analysis Streamlit Page

1️⃣ Page Setup
st.set_page_config(page_title="Facility Analytics Dashboard", layout="wide")
st.title("🏢 Facility Usage & Overcrowding Risk Dashboard")


Sets up the Streamlit page layout to wide for better visuals.

Adds a title to the dashboard.

2️⃣ Data Loading
df = get_table("facility_logs")


Loads your facility log data from your database using get_table().

The dataset contains columns like:

date

facility_name

duration_hr

crowding_index

is_weekend

user_type, zone, etc.

3️⃣ Data Cleaning & Type Casting
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["month"] = df["date"].dt.to_period("M").astype(str)
df["check_in_time"] = pd.to_datetime(df["check_in_time"], format="%H:%M", errors="coerce")
df["check_out_time"] = pd.to_datetime(df["check_out_time"], format="%H:%M", errors="coerce")
df_full = df.copy()


Ensures proper datetime formats for date/time columns.

Creates a month column for grouping/visualizations.

Keeps a full copy (df_full) for forecasting, so filtering in the dashboard doesn’t affect the model.

4️⃣ Overcrowding Risk Classification
OVERCROWD_THRESHOLD = 1.5
df_full["overcrowded"] = (df_full["crowding_index"] > OVERCROWD_THRESHOLD).astype(int)


Any facility with a crowding_index > 1.5 is considered overcrowded.

Creates a binary target variable overcrowded for classification.

Train Overcrowding Model

Features used: ["is_weekend", "facility_capacity", "special_event", "temperature", "avg_duration_today"].

Trains a RandomForestClassifier to predict overcrowding risk.

Stores predicted risk in:

df_full["predicted_overcrowding_risk"]


This is 1 (overcrowded) or 0 (not overcrowded).

5️⃣ Month Range Slider for Dashboard Filtering
start_date, end_date = st.sidebar.slider(...)
df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]


Adds a slider in the sidebar to filter visuals by date.

Important: This only filters charts, it does not affect forecasting.

Predicted overcrowding is merged from full dataset to the filtered view.

6️⃣ KPI Metrics
st.metric("Total Logs", f"{len(df):,}")
st.metric("Unique Facilities", f"{df['facility_name'].nunique():,}")
st.metric("Avg Feedback Rating", f"{df['feedback_rating'].mean():.2f}")


Displays three key metrics:

Total logs (formatted with commas)

Unique facilities

Average feedback rating (2 decimal places)

7️⃣ Charts
Chart 1: Monthly Usage
usage_monthly = df.groupby(["month", "facility_name"])["duration_hr"].sum().reset_index()
fig1 = px.line(...)


Shows total usage hours per facility over months.

Line chart with markers.

Chart 2: Usage by User Type

Grouped by facility_name and user_type.

Displays stacked/grouped bar chart.

Chart 3: Zone-Based Usage

Shows Indoor vs Outdoor usage per facility.

Chart 4: Feedback vs Crowding

Scatter plot of feedback_rating vs crowding_index.

Size of the marker = crowding_index.

Shows correlation between feedback and crowding.

Chart 5: Predicted Overcrowding Risk
df["predicted_overcrowding_risk_pct"] = df["predicted_overcrowding_risk"] * 100
overcrowd_monthly = df.groupby(["month", "facility_name"])["predicted_overcrowding_risk_pct"].sum().reset_index()


Aggregates predicted overcrowding per month in percentage.

Shows line chart with markers.

8️⃣ Forecasting Overcrowding Risk (Next 6 Months)
overcrowd_hist = df_full.groupby([df_full["date"].dt.to_period("M"), "facility_name"])["overcrowded"].mean().reset_index()


Computes historical average overcrowding per facility per month.

Uses three models for forecasting:

Linear Regression

Random Forest Regressor

K-Nearest Neighbors Regressor

ensemble_pred = (preds_lr + preds_rf + preds_knn) / 3
ensemble_pred = np.clip(ensemble_pred, 0, 1)


Forecast = ensemble average of three models.

Forecast is clipped to [0,1] → converted to percentage for display.

future_months = pd.period_range(start=last_period + 1, periods=6, freq="M").astype(str)


Forecasts next 6 months beyond the latest historical month.

9️⃣ Key Points

Month slider only affects visuals, not predictions.

Predicted Overcrowding Risk is binary (0 or 1) but visualized as percentage.

Forecasted risk is a continuous value (0-1) for the next 6 months.

Ensemble forecasting uses historical trends per facility.

Charts include line charts with markers, scatter plots, and bar charts.

✅ Overall Flow:

Load data → clean → create month column

Train overcrowding classifier on full history

Add month filter slider for chart visuals

Show KPIs & multiple charts

Compute historical risk and forecast next 6 months using ensemble models

