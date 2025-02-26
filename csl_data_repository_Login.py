#!/home/cslgipuzkoa/virtual_machine_disk/anaconda3/envs/SCP_test/bin/python
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
from flask import Flask, send_file
import subprocess
import webbrowser
import json

# Create a Flask server
server = Flask(__name__)

# Create a Dash app
app = dash.Dash(__name__, server=server)

# Get a list of all files and subfolders
root_dir = os.getcwd()

print('listdir')
print(os.listdir(root_dir))
print()
print('list')
tmp =[file for file in os.listdir(root_dir) if file not in ["Downloads_with_Login", "csl_data_repository_Login.py", "csl_data_repository.py"]][:]
print(tmp)

controls = [
    dcc.Dropdown(
        id="dropdown",
        options=[file for file in os.listdir(root_dir) if file not in ["Downloads_with_Login", "csl_data_repository_Login.py", "csl_data_repository.py"]],
        #options=os.listdir(root_dir),
        value='',
        style={"width": "400px",
               'marginLeft': '10px'}
    )
]

# Define the layout of the app
app.layout = html.Div([
    html.H1('City Science Lab@Gipuzkoa data repository', style={'font-size': '36px', 'font-family': 'Arial', 'font-weight': 'bold', 'color': '#00698f', 'margin-top': '10px'}),
    html.Hr(),
    html.H1("File Browser", style={'font-size': '24px',
                                   'font-family': 'Arial',
                                   'font-weight': 'bold',
                                   'color': '#00698f',
                                   'marginLeft': '10px', }),
    html.Div(controls),
    html.Div(id="folder-files"),
    dcc.Download(id='download-data_0'),

    # Login form
    html.Hr(),
    html.Div([
        html.Label('Username:'),
        dcc.Input(id='username', type='text'),
        html.Label('Password:'),
        dcc.Input(id='password', type='password'),
        html.Button('Login', id='login-button', n_clicks=0),
        html.Ul(id='download-with-login', style={'display': 'block'})
    ]),
    # Download option for logged-in user

    html.Hr(),
    #html.Label('Upload a file', style={'font-size': '24px',
    #                                    'font-family': 'Arial',
    #                                    'font-weight': 'bold',
    #                                    'marginLeft': '10px', }),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.A('Upload Files', style={'font-size': '24px',
                                          'font-family': 'Arial',
                                          'font-weight': 'bold',
                                          'color': '#00698f',
                                          'marginTop': '10px',
                                          'marginLeft': '10px',
                                          'cursor': 'pointer'}
                                          ),
        ])
    ),
    html.Div(id='upload-output'),
    html.Hr(),

    html.Div([
        html.Label('External data repositories:', style={'font-size': '24px'}),
        html.Ul([
            html.Li(html.A('MITMA', href='https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data/opendata-movilidad')),
            html.Li(html.A('Municipal data 1', href='https://www.eustat.eus/udalak/arbol_banco_municipal.aspx?id=All')),
            html.Li(html.A('Municipal data 2', href='https://www.euskadi.eus/web01-apudalma/es/t64amVisorWar/mapaGeo?R01HNoPortal=true&lan=0#')),
            html.Li(html.A('Income per "sección"', href='https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177088&menu=ultiDatos&idp=1254735976608'))
        ])
    ], style={'float': 'right', 'textAlign': 'left'}),

    html.P('Available disk space:', style={'font-size': '24px',
                                                     'marginLeft': '10px', }),
    html.Pre(id='disk-space', style={'font-size': '18px',
                                     'marginLeft': '10px'
                                     }),

    dcc.Interval(id='interval-component', interval=10000, n_intervals=0),
    dcc.Store(id="download-data")
],
style={
    'background-image': 'url(/assets/txindoki-aralar.jpg)',
    'font-family': 'Arial',
    'font-size': '20px',
    'background-size': 'cover',
    'height': '100vh',
    'margin': '0',
    'padding': '0',
    'border': '0',
    'position': 'absolute',
    'top': '0',
    'left': '0',
    'width': '100%',
    'height': '100%'
}

)

# Login callback
@app.callback(
    [Output('download-with-login', 'children')
     ],
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if n_clicks is not None and n_clicks > 0:
        if username == 'CSLGipuzkoa' and password == 'CSLGip.2023':  # Replace with your own authentication logic
            download_dir = os.path.join(root_dir, 'Downloads_with_Login')
            files = os.listdir(download_dir)
            children = [
                html.Li([
                    html.A(file, href=f"/download/{file}"),
                    dcc.Download(id=f"download-{file}")
                ]) for file in files
            ]
            return [children]
    else:
        # Reset the state of the login form and downloadable files section
        return []

@app.server.route("/download/<file>")
def download_file(file):
    download_dir = os.path.join(root_dir, 'Downloads_with_Login')
    return send_file(os.path.join(download_dir, file), as_attachment=True)


@app.callback(
    Output('upload-output', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        # Define the destination directory
        upload_dir = root_dir

        # Create the directory if it doesn't exist
        import os
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the file to the destination directory
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(contents.encode())
        return 'File uploaded successfully!'
    return ''



@app.callback(
    Output('disk-space', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_disk_space(n):
    output = subprocess.check_output(['df', '-h'])
    return output.decode('utf-8')


@app.callback(
    Output("folder-files", "children"),
    [Input("dropdown", "value")],
    prevent_initial_call=True
)
def list_all_files(file_names):
    if file_names is None:
        return None
    if os.path.isdir(file_names):
        #files = os.listdir(file_names)
        files = [file for file in os.listdir(file_names) if file not in ["Downloads_with_Login", "csl_data_repository_Login.py", "csl_data_repository.py"]],
        file_list = html.Div([
            html.Ul([
                html.Li([
                    html.Div([
                        html.Span(f"{file} "),
                        html.Button("Download", id={"type": "download-button", "index": str(ii)}, n_clicks=0)
                    ], style={"display": "inline-block"})
                ]) for ii, file in enumerate(files)
            ])
        ])
        print('trying to send updated dropdown options')
        print('file_list:', file_list)
        return file_list

    else:
        file_list = html.Div([
            html.Ul([
                html.Li([
                    html.Div([
                        html.Span(f"{file_names} "),
                        html.Button("Download", id={"type": "download-button", "index": str(0)}, n_clicks=0)
                    ], style={"display": "inline-block"})
                ])
            ])
        ])
        return file_list
    #    return None

@app.callback(
    Output("download-data_0", "data"),
    [Input({"type": "download-button", "index": dash.dependencies.ALL}, "n_clicks")],
    [dash.dependencies.State("dropdown", "value")]
)
def download_file(n_clicks, file_names):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    props = ctx.triggered[0]["prop_id"].split(".")
    print()
    print('new callback')
    print('input_id:', input_id)
    print('props:', props)
    print('ctx:', ctx.triggered)
    print('file_names:',file_names)
    print('n_clicks:',n_clicks)
    if ctx.triggered[0]['value']==1:
        props = ctx.triggered[0]["prop_id"].split(".")
        print(props)
        prop_id = props[0]
        print('prop_id:', prop_id)
        index = json.loads(prop_id)['index']
        file_index = int(index)
        print('file_index:', file_index)
        try:
            #files = os.listdir(file_names)
            files = [file for file in os.listdir(file_names) if file not in ["Downloads_with_Login", "csl_data_repository_Login.py", "csl_data_repository.py"]],
            print('files:', files)
            file_name = files[file_index]
            print('file_name:', file_name)
            for root, dirs, files in os.walk(root_dir):
                if file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_file_path = os.path.relpath(file_path)
                    break
            print('file_path:', file_path)
            print('rel_file_path:', rel_file_path)
        except:
            file_name = file_names
            print('file_name:', file_name)
            file_path = os.path.join(root_dir, file_name)

        if os.path.isfile(file_path):
            return dcc.send_file(file_path)
        else:
            return "Error: The selected item is not a file."
    return None


@app.callback(
    Output("dropdown", "options"),
    [Input("upload-data", "filename")]
)
def update_dropdown_options(filename):
    options=[file for file in os.listdir(root_dir) if file not in ["Downloads_with_Login", "csl_data_repository_Login.py", "csl_data_repository.py"]],
    #return os.listdir(root_dir)
    return options[0]

# Run the app on port 6556
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=6556)
    #ssl_context = ('/home/cslgipuzkoa/virtual_machine_disk/Data_repository/example.crt','/home/cslgipuzkoa/virtual_machine_disk/Data_repository/example.key')
    #app.run_server(host='0.0.0.0', port=6556, ssl_context=ssl_context,debug=True)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ~                                                                                            