from flask import Flask, render_template, request, jsonify
from main import generate_questions

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        params = {
            "subject": request.form.get('subject', '高等数学'),
            "difficulty": request.form.get('difficulty', '中等'),
            "question_type": request.form.get('question_type', '选择题'),
            "num": int(request.form.get('num', 3))
        }

        result = generate_questions(**params)
        return jsonify({
            "status": "success" if result else "error",
            "data": result.get('questions', []) if result else []
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


@app.route('/generate_full', methods=['POST'])
def generate_full():
    """修改点：完整试卷生成逻辑优化"""
    try:
        req_data = {
            "subject": request.form['subject'],
            "difficulty": request.form['difficulty'],
            "choice_num": int(request.form.get('choice_num', 0)),
            "blank_num": int(request.form.get('blank_num', 0)),
            "calc_num": int(request.form.get('calc_num', 0))
        }

        paper = {
            "meta": {
                "subject": req_data['subject'],
                "difficulty": req_data['difficulty'],
                "total_score": req_data['choice_num'] * 5 + req_data['blank_num'] * 3 + req_data['calc_num'] * 10
            },
            "sections": []
        }

        # 生成选择题（新增参数严格校验）
        if req_data['choice_num'] > 0:
            choice_result = generate_questions(
                req_data['subject'],
                req_data['difficulty'],
                "选择题",
                req_data['choice_num']
            )
            if choice_result:
                paper['sections'].append({
                    "type": "选择题",
                    "questions": choice_result.get('questions', []),
                    "score": 5
                })

        # 其他题型生成逻辑保持不变...
        # 填空题
        if req_data['blank_num'] > 0:
            blank_result = generate_questions(
                req_data['subject'],
                req_data['difficulty'],
                "填空题",
                req_data['blank_num']
            )
            if blank_result:
                paper['sections'].append({
                    "type": "填空题",
                    "questions": blank_result.get('questions', []),
                    "score": 3
                })

        # 计算题
        if req_data['calc_num'] > 0:
            calc_result = generate_questions(
                req_data['subject'],
                req_data['difficulty'],
                "计算题",
                req_data['calc_num']
            )
            if calc_result:
                paper['sections'].append({
                    "type": "计算题",
                    "questions": calc_result.get('questions', []),
                    "score": 10
                })

        return jsonify({"status": "success", "data": paper})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)