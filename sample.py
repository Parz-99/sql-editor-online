# type: ignore
from flask import Flask,render_template,url_for,request
import sqlite3
import pandas as pd
import re
conn = sqlite3.connect('data/world.sqlite',check_same_thread=False)
c = conn.cursor()

#func to execute a query
# def sql_executor(raw_query):
#     c.execute(raw_query)
#     data = c.fetchall()
#     return data

def sql_executor(queries):
    results = []
    errors = []
    success_queries = []
    for query in queries:
        try:
            c.execute(query)
            success_queries.append(query)
        except Exception as e:
            # Handle the exception here
            error_message = f"Error executing SQL query: {e}"
            errors.append({'error': error_message})
        data = c.fetchall()
        results.append(data)
    

    return {'results': results, 'errors': errors, 'success_queries':success_queries}



def remove_comments(sql):
    # Remove SQL comments (both single-line and multi-line)
    sql = re.sub(r'(--[^\n]*)|(/\*.*?\*/)', '', sql, flags=re.DOTALL)
    return sql.strip()


#init app
app = Flask(__name__)

#routes
@app.route('/')
def index():
    results = pd.DataFrame([])
    errors = pd.DataFrame([])
    return render_template('index.html',results = results,errors = errors)

@app.route('/process_query',methods=['GET','POST'])
def process_query():
    if request.method == 'POST':
        raw_query = request.form['raw_query']
        raw_query = remove_comments(raw_query)
        queries = [query.strip() for query in raw_query.split(';') if query.strip()]
        initial_results = sql_executor(queries)
        num_columns = [len(item) for sublist in initial_results['results'] for item in sublist]
        num_columns = num_columns[0] if num_columns else None
        print("Required Length is : ",num_columns)
        # Generate column names with numbers
        results1 = initial_results['results']
        success_queries = initial_results['success_queries']
        results = pd.DataFrame(initial_results['results'])
        print("initial data",initial_results['results'])
        print(results)
        res_final = []
        for res in results1:
            res_final.append(pd.DataFrame(res))
        styled_html = []
        for res in res_final:
            styled_html.append(res.style.set_table_styles([{'selector': 'th', 'props': [('border', '1px solid black')]},
            {'selector': 'td, th', 'props': [('border-collapse', 'collapse'), ('border', '1px solid black'), ('padding', '8px')]},
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            ]))
#         styled_html = res_final.style.set_table_styles([
#     {'selector': 'th', 'props': [('border', '1px solid black')]},
#     {'selector': 'td, th', 'props': [('border-collapse', 'collapse'), ('border', '1px solid black'), ('padding', '8px')]},
#     {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
# ])
       
        errors = pd.DataFrame(initial_results['errors'])
        print("Errors are: ", errors)
        #,results = styled_html
    return render_template('index.html',results=styled_html,raw_query = raw_query,success_queries = success_queries,errors = errors)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)