from flask import Flask, render_template, request, jsonify
from main import generate_questions

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False



# =========== 定义根路由，用于渲染主页 ===========
@app.route('/')
def index():
    return render_template('index.html')

# =========== 定义生成完整试卷的路由 =======================================================================================
@app.route('/generate_full', methods=['POST'])
def generate_full():
    try:
        # 从表单获取(科目 难度  选择题数量 填空题数量 计算题题数量)
        req_data = {
            "subject": request.form['subject'],
            "difficulty": request.form['difficulty'],
            "choice_num": int(request.form.get('choice_num', 0)),
            "blank_num": int(request.form.get('blank_num', 0)),
            "calc_num": int(request.form.get('calc_num', 0))
        }

        # 初始化试卷结构(科目 难度 总分)
        paper = {
            "meta": {
                "subject": req_data['subject'],
                "difficulty": req_data['difficulty'],
                "total_score": req_data['choice_num'] * 5 + req_data['blank_num'] * 3 + req_data['calc_num'] * 10
            },
            "sections": []
        }

        # 生成选择题
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
        # 以JSON格式返回生成的试卷信息
        return jsonify({"status": "success", "data": paper})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)