from flask import Flask ,render_template,url_for,request,session,redirect,flash
from flask_pymongo import PyMongo
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
import bcrypt
from dict import Dict
import csv
from recommendation import Recommendation
import requests
from requests.auth import HTTPDigestAuth
from ipify import get_ip


app = Flask(__name__)
app.config['MONGO_DBNAME'] ='prs'
app.config['MONGO_URI'] ='mongodb+srv://shubh:shubh@prs-2b90z.mongodb.net/User?retryWrites=true'
app.config.from_pyfile('config.cfg')
app.config['SECRET_KEY']='secretkey'

mail= Mail(app)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])


mongo= PyMongo(app)

python = Dict.python

cpp =Dict.cpp

javatutpython=Dict.javatutpython

c=Dict.c
tanishq =[]
def loadcsv():

    with open('static/output.csv', 'r', encoding = 'utf-8') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            tanishq.append(row)

@app.route("/")
@app.route("/index")
def home():
    return render_template('index.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email_from_token = s.loads(token,salt='email-confirm',max_age=300)

    except SignatureExpired:
        return 'The link is expired'
    users=mongo.db.user

    users.update_one({'email':email_from_token},{"$set":  {'email_confirmation':'1'}})

    return 'email verified'

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name=request.form["username"]
        email=request.form["email"]
        password=bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
        country=request.form["country"]

        if name[0].isdigit():
            return "username should start with a character"

        base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
        GROUP_ID = '5c9871e2553855b52c5fafb3'
        whitelist_ep = "/groups/" + GROUP_ID + "/whitelist"
        url = '{}{}'.format(base_url, whitelist_ep)

        ip = get_ip()

        r =requests.post(
            url,
            auth=HTTPDigestAuth('shubhambhawsar63@gmail.com', '1532581d-4a2e-4711-8d63-f2e2f7f2a6df'),
            json=[{'ipAddress': ip, 'comment': 'test'}]  # the comment is option
            )


        users=mongo.db.user
        existing_username = users.find_one({'username': name})
        existing_email = users.find_one({'email':email})

        if existing_username is None and existing_email is None:

            email=request.form['email']
            token=s.dumps(email, salt='email-confirm')

            msg= Message('Confirm Email' ,sender='helloheroguy@gmail.com' , recipients=[email])

            link = url_for('confirm_email',token=token,_external=True)

            msg.body = 'your link is {}'.format(link)

            mail.send(msg)
            users.insert_one({
            'username':name,
            'email':email,
            'password':password,
            'country':country,
            'email_confirmation':'0',
            'recommendation':'-1'
            })
            session['username']=name
            return redirect(url_for('survey'))
        else:
            if existing_email:
                return 'email already in use'
            if existing_username:
                return 'username not available'
    return render_template('signup.HTML')


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        name=request.form["username"]

        users=mongo.db.user
        login_user = users.find_one({'username': name})
        if login_user:
            if bcrypt.hashpw(request.form["password"].encode('utf-8'),login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                flash("login sucessful")
                return redirect(url_for('loginrdr'))

        return 'invalid username/password combo'
    else:

        return render_template("LogIn.HTML")

@app.route("/recommend",methods=["POST"])
def recommendation_sys():
    inp1=int(request.form["experience"])
    inp2=int(request.form["influence"])
    inp3=int(request.form["days"])
    inp4=int(request.form["time"])
    recommended = Recommendation.recommend(inp1,inp2,inp3,inp4)
    h = int(round(recommended[0]))
    info=Dict.courses[h]

    name = session['username']

    users=mongo.db.user
    users.update_one({'username':name},{"$set":  {'recommendation':h}})

    return redirect(url_for('courses'))

@app.route("/signout")
def signout():
    session.pop('username')
    session.clear()
    return redirect(url_for('signup'))

@app.route("/loginrdr",methods=["POST","GET"])
def loginrdr():

    return redirect('index')

@app.route("/courses")
def courses():
    recommend=None
    users=mongo.db.user

    if not session:
        return redirect(url_for('login'))
    name=session['username']

    exist_user=users.find_one({'username': name})
    if exist_user['recommendation'] != -1:
        recommend = exist_user['recommendation']
        info=Dict.courses[recommend]
    return render_template('courses.html',info=info,recommend=recommend)


@app.route("/forum")
def forum():
    return render_template('forum.html')


@app.route("/survey")
def survey():
    return render_template('survey.html')

@app.route("/python_forum")
def py_forum():
    return render_template('python_forum.html')


@app.route("/python_courses")
def python_courses():
    return render_template('courses/python_courses.html')

#cpp Pages

@app.route("/cpp_introduction")
def cpp_introduction():
    return render_template('CPP/Introduction.html',topics=cpp)

@app.route("/cpp_program_structure")
def cpp_structure():
    return render_template('CPP/Structure.html',topics=cpp)

@app.route("/cpp_input_output")
def cpp_io():
    return render_template('CPP/Input_Output.html',topics=cpp)

@app.route("/cpp_basics")
def cpp_basics():
    return render_template('CPP/Basics.html',topics=cpp)

@app.route("/cpp_data_types")
def cpp_dataType():
    return render_template('CPP/Data_types.html',topics=cpp)

@app.route("/cpp_constants")
def cpp_constants():
    return render_template('CPP/Constants.html',topics=cpp)

@app.route("/cpp_operator")
def cpp_operator():
    return render_template('CPP/Operators.html',topics=cpp)

@app.route("/cpp_control_statements")
def cpp_control():
    return render_template('CPP/Control_Statements.html',topics=cpp)

@app.route("/cpp_array")
def cpp_array():
    return render_template('CPP/Arrays.html',topics=cpp)

@app.route("/cpp_strings")
def cpp_strings():
    return render_template('CPP/Strings.html',topics=cpp)

@app.route("/cpp_functions")
def cpp_functions():
    return render_template('CPP/Functions.html',topics=cpp)

@app.route("/cpp_parameter_passing")
def cpp_parameter():
    return render_template('CPP/Parameter_Passing.html',topics=cpp)

@app.route("/cpp_class_object")
def cpp_class_object():
    return render_template('CPP/Class_object.html',topics=cpp)

@app.route("/cpp_constructor_destructor")
def cpp_const_dest():
    return render_template('CPP/Constructor_Destructor.html',topics=cpp)

@app.route("/cpp_op_overloading")
def cpp_op_overloading():
    return render_template('CPP/Operator_Overloading.html',topics=cpp)

@app.route("/cpp_type_conversion")
def cpp_type_conversion():
    return render_template('CPP/Type_conversion.html',topics=cpp)

@app.route("/cpp_inheritance")
def cpp_inheritance():
    return render_template('CPP/Inheritance.html',topics=cpp)

@app.route("/cpp_types_inheritance")
def cpp_types_inheritance():
    return render_template('CPP/Types_Inheritance.html',topics=cpp)

@app.route("/cpp_polymorphism")
def cpp_poly():
    return render_template('CPP/Polymorphism.html',topics=cpp)

@app.route("/cpp_abstact_class")
def cpp_abstract_class():
    return render_template('CPP/Abstract_class.html',topics=cpp)

@app.route("/cpp_file_handling")
def cpp_file():
    return render_template('CPP/File_Handling.html',topics=cpp)

@app.route("/cpp_exception_handling")
def cpp_exception_handling():
    return render_template('CPP/Exception_Handling.html',topics=cpp)

#java tutorial python
@app.route("/jtpython_overview")
def pythonCourses():
    loadcsv()
    return render_template('javatutorials/python/introduction.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_environment_setup")
def jtpythonenvsetup():
    loadcsv()
    return render_template('javatutorials/python/env_setup.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_basic_syntax")
def jtpythonbasic():
    loadcsv()
    return render_template('javatutorials/python/basicsyntax.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_variable_types")
def jtpythonvar():
    loadcsv()
    return render_template('javatutorials/python/vartype.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_basic_operators")
def jtpythonop():
    loadcsv()
    return render_template('javatutorials/python/operators.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_decision_making")
def jtpythondecision():
    loadcsv()
    return render_template('javatutorials/python/decision.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_loops")
def jtpythonloops():
    loadcsv()
    return render_template('javatutorials/python/loops.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_numbers")
def jtpythonnumbers():
    loadcsv()
    return render_template('javatutorials/python/numbers.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_strings")
def jtpythonstrings():
    loadcsv()
    return render_template('javatutorials/python/strings.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_list")
def jtpythonlist():
    loadcsv()
    return render_template('javatutorials/python/list.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_tuples")
def jtpythontuple():
    loadcsv()
    return render_template('javatutorials/python/tuples.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_dictionary")
def jtpythondict():
    loadcsv()
    return render_template('javatutorials/python/dictionary.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_date_and_time")
def jtpythondate():
    loadcsv()
    return render_template('javatutorials/python/datetime.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_functions")
def jtpythonfunc():
    loadcsv()
    return render_template('javatutorials/python/functions.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_modules")
def jtpythonmodules():
    loadcsv()
    return render_template('javatutorials/python/modules.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_files_io")
def jtpythonio():
    loadcsv()
    return render_template('javatutorials/python/files_io.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_exceptions_handling")
def jtpythonexception():
    loadcsv()
    return render_template('javatutorials/python/exception.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_object_oriented")
def jtpythonoo():
    loadcsv()
    return render_template('javatutorials/python/objectoriented.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_regular_expressions")
def jtpythonre():
    loadcsv()
    return render_template('javatutorials/python/regularexpressions.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_cgi_programming")
def jtpythoncgi():
    loadcsv()
    return render_template('javatutorials/python/cgi.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_mysql_databases_access")
def jtpythondatabase():
    loadcsv()
    return render_template('javatutorials/python/database.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_network_programming")
def jtpythonnetwork():
    loadcsv()
    return render_template('javatutorials/python/network.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_sending_email_using_smtp")
def jtpythonemail():
    loadcsv()
    return render_template('javatutorials/python/email.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_multithreaded_programming")
def jtpythonthread():
    loadcsv()
    return render_template('javatutorials/python/multithreading.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_xml_processing")
def jtpythonxml():
    loadcsv()
    return render_template('javatutorials/python/xml.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_gui_programming")
def jtpythongui():
    loadcsv()
    return render_template('javatutorials/python/gui.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_extension_programming_with_c")
def jtpythonext():
    loadcsv()
    return render_template('javatutorials/python/ext.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_questions_and_answers")
def jtpythonqa():
    loadcsv()
    return render_template('javatutorials/python/qa.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_quick_guide")
def jtpythonguide():
    loadcsv()
    return render_template('javatutorials/python/guide.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_tools")
def jtpythontools():
    loadcsv()
    return render_template('javatutorials/python/tools.html',topics=javatutpython,python=tanishq)

@app.route("/jtpython_useful_resources")
def jtpythonres():
    loadcsv()
    return render_template('javatutorials/python/res.html',topics=javatutpython,python=tanishq)


# python pages
@app.route("/python_introduction")
def py_introduction():
    return render_template('F_Python/Introduction.html',topics=python)

@app.route("/python_Variable_and_Keywords")
def py_Var_Key():
    return render_template('F_Python/Variables_Keywords.html',topics=python)

@app.route("/python_Types")
def py_types():
    return render_template('F_Python/Types.html',topics=python)

@app.route("/python_Operators")
def py_operators():
    return render_template('F_Python/Operators.html',topics=python)

@app.route("/python_Expressions")
def py_expressions():
    return render_template('F_Python/Expressions.html',topics=python)

@app.route("/python_Control_Statements")
def py_cont_stat():
    return render_template('F_Python/Control_Statements.html',topics=python)

@app.route("/python_Data_Structure")
def py_ds():
    return render_template('F_Python/Data_Structures.html',topics=python)

@app.route("/python_Functions")
def py_functions():
    return render_template('F_Python/Functions.html',topics=python)

@app.route("/python_Modules")
def py_mpdules():
    return render_template('F_Python/Modules.html',topics=python)

@app.route("/python_Packages")
def py_packages():
    return render_template('F_Python/Packages.html',topics=python)

@app.route("/python_Object_Oriented_Programming")
def py_oop():
    return render_template('F_Python/oop.html',topics=python)

@app.route("/python_Exceptions")
def py_exceptions():
    return render_template('F_Python/Exception.html',topics=python)

@app.route("/python_Standard_Library")
def py_st_lib():
    return render_template('F_Python/Standard_Library.html',topics=python)

@app.route("/python_Testing")
def py_testing():
    return render_template('F_Python/Testing.html',topics=python)

#C LINKS

@app.route("/c_computer_basics")
def c_computer_basics():
	return render_template('c/basics_computer.html',topics=c)
@app.route("/c_software_concepts")
def c_software_concepts():
	return render_template('c/software_concepts.html',topics=c)
@app.route("/c_steps_for_program")
def c_steps_for_program():
	return render_template('c/steps_program.html',topics=c)

@app.route("/c_introduction_to_c")
def c_introduction_to_c():
	return render_template('c/introduction.html',topics=c)
@app.route("/c_creating_and_running_c")
def c_creating_and_running_c():
	return render_template('c/creating_c_programs.html',topics=c)

@app.route("/c_tokens")
def c_tokens():
	return render_template('c/tokens.html',topics=c)
@app.route("/c_data_types")
def c_data_types():
	return render_template('c/data_types.html',topics=c)
@app.route("/c_operators")
def c_operators():
	return render_template('c/operators.html',topics=c)
@app.route("/c_expressions")
def c_expressions():
	return render_template('c/Expressions.html',topics=c)
@app.route("/c_type_casting")
def c_type_casting():
	return render_template('c/type_casting.html',topics=c)
@app.route("/c_decision_making_statements")
def c_decision_making_statements():
	return render_template('c/decision.html',topics=c)
@app.route("/c_iteration_statements")
def c_iteration_statements():
	return render_template('c/iteration.html',topics=c)
@app.route("/c_arrays")
def c_arrays():
	return render_template('c/array.html',topics=c)
@app.route("/c_strings")
def c_strings():
	return render_template('c/Strings.html',topics=c)
@app.route("/c_functions")
def c_functions():
	return render_template('c/functions.html',topics=c)
@app.route("/c_predefined_libraries")
def c_predefined_libraries():
	return render_template('c/predefined_functions.html',topics=c)
@app.route("/c_nested_functions")
def c_nested_functions():
	return render_template('c/Nested_functions.html',topics=c)
@app.route("/c_types_of_variables")
def c_types_of_variables():
	return render_template('c/types_variables.html',topics=c)
@app.route("/c_storage_classes")
def c_storage_classes():
	return render_template('c/Storage_classes.html',topics=c)
@app.route("/c_passing_array_to_functions")
def c_passing_array_to_functions():
	return render_template('c/passing_array2func.html',topics=c)
@app.route("/c_preprocessor_directives")
def c_preprocessor_directives():
	return render_template('c/preprocessor_directives.html',topics=c)
@app.route("/c_pointers")
def c_pointers():
	return render_template('c/pointers.html',topics=c)
@app.route("/c_structures")
def c_structures():
	return render_template('c/Structures.html',topics=c)
@app.route("/c_union")
def c_union():
	return render_template('c/union.html',topics=c)
@app.route("/c_file_management")
def c_file_management():
	return render_template('c/file_management.html',topics=c)
@app.route("/c_command_line_argument")
def c_command_line_argument():
	return render_template('c/command_line_arg.html',topics=c)




if __name__ == '__main__':

    app.run(debug=True)
