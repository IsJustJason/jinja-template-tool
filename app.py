from flask import Flask, render_template, request, flash, redirect, url_for
import yaml
from jinja2 import Template
import os

app = Flask(__name__)
app.secret_key = 'super secret key'  # Needed for flash messaging

# Folder to save templates and variables
SAVE_DIR = "saved_templates"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the YAML content and the Jinja template from the form
        yaml_content = request.form.get('yaml_content')
        jinja_template = request.form.get('jinja_template')
        template_name = request.form.get('template_name')
        
        # Save the variables and template if a name is given
        if template_name:
            with open(os.path.join(SAVE_DIR, f"{template_name}_vars.yaml"), 'w') as f:
                f.write(yaml_content)
            with open(os.path.join(SAVE_DIR, f"{template_name}_template.jinja"), 'w') as f:
                f.write(jinja_template)
            flash('Template and variables saved successfully!', 'success')

        try:
            # Parse the YAML content
            variables = yaml.safe_load(yaml_content)
            
            # Render the template
            template = Template(jinja_template)
            rendered_template = template.render(variables)
        except yaml.YAMLError as e:
            flash(f'Invalid YAML content: {e}', 'error')
            rendered_template = ''
        except Exception as e:
            flash(f'Error rendering template: {e}', 'error')
            rendered_template = ''

        return render_template('index.html', rendered_template=rendered_template)
    
    return render_template('index.html', rendered_template='')

# Additional route to get the saved templates content
@app.route('/get_template/<template_name>')
def get_template(template_name):
    try:
        with open(os.path.join(SAVE_DIR, f"{template_name}_vars.yaml"), 'r') as f:
            yaml_content = f.read()
        with open(os.path.join(SAVE_DIR, f"{template_name}_template.jinja"), 'r') as f:
            jinja_template = f.read()
    except FileNotFoundError:
        return {'error': 'Template not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

    return {'yaml_content': yaml_content, 'jinja_template': jinja_template}

# Route to list saved templates
@app.route('/saved_templates')
def saved_templates():
    templates = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith('_vars.yaml'):
            templates.append(filename[:-10])  # Remove the suffix to get the template name
    return render_template('saved_templates.html', templates=templates)

if __name__ == '__main__':
    app.run(debug=True)
