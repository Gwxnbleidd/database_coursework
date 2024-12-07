from unicodedata import category

from sqlalchemy.orm import Session

from database.engine import get_engine
from database import querys
from flask import Flask, render_template, request, session

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main_page():
    return render_template('main.html')


@app.route('/get/childs/all', methods=['GET'])
def get_table_childs():
    with Session(get_engine()) as session:
        headers, childs = querys.get_all_childs(session)

    return render_template('table_childs.html', headers=headers, childs=childs)

@app.route('/get/childs/<int:c_id>', methods=['GET'])
def get_special_child(c_id: int):
    with Session(get_engine()) as session:
        return querys.get_child(session, c_id)

@app.route('/get/childs/attending_du', methods=['GET'])
def get_table_childs_attending_du():
    with Session(get_engine()) as session:
        headers, childs = querys.get_childs_attending_DU(session)

    for i in range(0, len(childs), 2):
        childs[i]['mather'], childs[i]['mather_info'] = childs[i + 1]['par_fio'], childs[i + 1]['par_info']
    childs = childs[0::2]

    return render_template('main_table_childs.html', headers=headers[:-3], childs=childs)


@app.route('/get/childs/in_queue', methods=['GET'])
def get_table_childs_in_queue():
    with Session(get_engine()) as session:
        headers, childs = querys.get_childs_in_queue(session)

    return render_template('table_childs.html', headers=headers, childs=childs)


@app.route('/get/childs/special_du/<int:du_id>', methods=['GET'])
def get_childs_from_special_du(du_id):
    with Session(get_engine()) as session:
        childs = querys.get_children_from_du(session, du_id)
    return childs


@app.route('/get/childs/special_du', methods=['GET'])
def get_table_childs_from_special_du():
    with Session(get_engine()) as session:
        _, DUs = querys.get_all_DU(session)

    return render_template('table_childs_from_special_du.html', DUs=DUs)


@app.route('/get/childs/needs_du_query', methods=['GET'])
def get_childs_needs_du():
    with Session(get_engine()) as session:
        age = request.args.get('age')
        category = request.args.get('category')
        return querys.get_children_need_du(session, age, category)


@app.route('/get/childs/needs_du', methods=['GET'])
def get_table_childs_needs_du():    
    return render_template('childs_needs_du.html')


@app.route('/get/du/all', methods=['GET'])
def get_table_du():
    with Session(get_engine()) as session:
        headers, DUs = querys.get_all_DU(session)

    return render_template('table_DUs.html', headers=headers, DUs=DUs)


@app.route('/get/du/free_places/<int:age>', methods=['GET'])
def get_table_du_free_places(age: int):
    with Session(get_engine()) as session:
        return querys.get_du_with_free_places(session, age)


@app.route('/get/du/free_places', methods=['GET'])
def get_du_free_places():
    return render_template('free_places_for_child_special_age.html')

@app.route('/child/update', methods=['GET', 'POST'])
def update_child():
    if request.method == 'GET':
        with Session(get_engine()) as session:
            _, childs = querys.get_all_childs(session)
            parents = querys.get_all_parents(session)
        
        mathers, fathers = [], []
        for parent in parents:
            if parent.get('rol') == 'мать':
                mathers.append(parent)
            else:
                fathers.append(parent)
        return render_template('change_data_about_child.html', childs=childs, mathers=mathers, fathers=fathers)

    data = request.form.to_dict()
    c_id, m_id, f_if = map(int,(data.get('id'), data.get('mather'), data.get('father')))
    with Session(get_engine()) as session:
        querys.update_info_about_children(session, c_id, m_id, f_if, data)
        return '200'

if __name__ == '__main__':
    app.run(debug=True)
