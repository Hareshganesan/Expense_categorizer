import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta

# Load category mappings
def load_categories():
    try:
        with open('categories.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'groceries': ['walmart', 'supermarket', 'grocery', 'aldi'],
            'rent': ['rent', 'apartment'],
            'utilities': ['electric', 'water', 'gas', 'internet'],
            'entertainment': ['netflix', 'cinema', 'movie', 'concert'],
            'other': []
        }

categories = load_categories()

# Categorization function
def categorize(description):
    description = description.lower()
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    return 'other'

# Streamlit UI
st.set_page_config(page_title="Expense Categorizer", page_icon="💰", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FF6347;'>💰 Expense Categorizer</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    with st.spinner("Processing your file..."):
        df = pd.read_csv(uploaded_file)

        # Validate columns
        if 'Description' not in df.columns or 'Amount' not in df.columns:
            st.error("CSV must contain 'Description' and 'Amount' columns.")
        else:
            # Clean and process data
            df.dropna(subset=['Description', 'Amount'], inplace=True)
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df.dropna(subset=['Amount'], inplace=True)
            df['Category'] = df['Description'].apply(categorize)

            # Add a Date column if missing
            if 'Date' not in df.columns:
                df['Date'] = [datetime.today() - timedelta(days=i) for i in range(len(df))]
            df['Date'] = pd.to_datetime(df['Date'])
            df['Month'] = df['Date'].dt.to_period('M')

            # Display categorized data
            st.write("### Categorized Expenses")
            st.dataframe(df)

            # Spending summary
            summary = df.groupby('Category')['Amount'].sum().reset_index()
            st.write("### Spending Summary")
            st.dataframe(summary.style.background_gradient(cmap='YlGnBu').format({'Amount': '${:,.2f}'.format}))

            # Savings Tips Function
            def saving_tips(category):
                tips = {
                    'groceries': "Consider buying in bulk, using coupons, and shopping at discount stores.",
                    'rent': "Try to negotiate a lower rent or consider moving to a more affordable place.",
                    'utilities': "Turn off unused electronics, and use energy-efficient appliances.",
                    'entertainment': "Cut down on subscriptions and find free or low-cost entertainment options.",
                    'other': "Analyze discretionary expenses and reduce non-essential spending."
                }
                return tips.get(category, "No tips available.")

            # Display Savings Suggestions
            st.write("### Expenditure Summary and Saving Tips")
            for _, row in summary.iterrows():
                category = row['Category']
                amount = row['Amount']
                st.write(f"*Category:* {category.capitalize()}, *Spent:* ${amount:.2f}")
                st.write(f"💡 *Saving Tip:* {saving_tips(category)}")
                st.markdown("---")

            # Bar chart for spending distribution
            st.write("### Bar Chart: Spending by Category")
            fig, ax = plt.subplots(figsize=(6, 6))
            sns.barplot(x='Category', y='Amount', data=summary, palette='viridis', ax=ax)
            ax.set_title('Spending by Category')
            ax.set_ylabel('Amount ($)')
            st.pyplot(fig, use_container_width=False)

            # Pie chart for spending distribution
            st.write("### Pie Chart: Spending Distribution")
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(summary['Amount'], labels=summary['Category'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
            ax.axis('equal')
            st.pyplot(fig, use_container_width=False)

            # Monthly Spending Trend
            monthly_spending = df.groupby('Month')['Amount'].sum().reset_index()
            st.write("### Monthly Spending Trend")
            fig, ax = plt.subplots(figsize=(4, 4))
            st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            ax.plot(monthly_spending['Month'].astype(str), monthly_spending['Amount'], marker='o', color='purple')
            ax.set_title('Monthly Spending Trend')
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount ($)')
            st.pyplot(fig, use_container_width=False)

            # Budget vs Actual Comparison
            st.write("### Budget vs Actual Comparison")
            budget_groceries = st.number_input("Groceries Budget ($)", min_value=0, value=200)
            budget_rent = st.number_input("Rent Budget ($)", min_value=0, value=1000)
            budget_utilities = st.number_input("Utilities Budget ($)", min_value=0, value=150)
            budget_entertainment = st.number_input("Entertainment Budget ($)", min_value=0, value=100)
            
            # Budget Dataframe
            budget_data = {
                'Category': ['groceries', 'rent', 'utilities', 'entertainment'],
                'Budget': [budget_groceries, budget_rent, budget_utilities, budget_entertainment],
                'Actual': [
                    df[df['Category'] == 'groceries']['Amount'].sum(),
                    df[df['Category'] == 'rent']['Amount'].sum(),
                    df[df['Category'] == 'utilities']['Amount'].sum(),
                    df[df['Category'] == 'entertainment']['Amount'].sum()
                ]
            }

            budget_df = pd.DataFrame(budget_data)

            # Bar chart for budget vs actual
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.bar(budget_df['Category'], budget_df['Budget'], label='Budget', alpha=0.6, color='orange')
            ax.bar(budget_df['Category'], budget_df['Actual'], label='Actual', alpha=0.6, color='green')
            ax.set_title('Budget vs Actual Spending')
            ax.set_ylabel('Amount ($)')
            ax.legend()
            st.pyplot(fig, use_container_width=False)

            # Total spent
            total_spent = summary['Amount'].sum()
            st.write(f"### Total Spent: *${total_spent:.2f}*")

            # Allow CSV download
            st.download_button(
                label="Download Categorized Data",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='categorized_expenses.csv',
                mime='text/csv')