import requests
import json
import time

# =================配置区域=================
API_KEY = "sk-6e6d266f347645d7b3bcca7370cf7a85"
BASE_URL = "https://api.deepseek.com/v1"
ENDPOINT = "/chat/completions"
MAX_RETRIES = 3
# =========================================

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def build_prompt(subject, difficulty, question_type, num):
    type_rules = {
        "选择题": f"""必须包含4个选项，格式示例：
                题目：[题干]（以？结尾）
                选项：
                A. [内容]
                B. [内容]
                C. [内容]
                D. [内容]
                答案：[字母]
                注意：生成的题目必须各不相同。""",
        "填空题": (
            "必须使用下划线'_'标记填空位置，示例：\n"
            "题目：二战爆发于____年\n"
            "答案：1939\n"
            "禁止出现任何选项标识"
        ),
        "简答题": (
            "要求答案结构完整，包含至少3个要点\n"
            "示例：\n"
            "题目：简述工业革命的影响\n"
            "答案：1. 促进生产力发展... 2. 改变社会结构... 3. 推动城市化进程..."
        ),
        "判断题": "答案只能为「正确」或「错误」",
        "计算题": (
            "必须满足以下要求：\n"
            "1. 包含至少两个带编号的小问，格式示例：\n"
            "   (1) 第一小问...?\n"
            "   (2) 第二小问...\n"
            "2. 题干或小问必须以以下形式结尾：\n"
            "   - 以问号?结尾\n"
            "   - 包含「求...的值」\n"
            "   - 包含「证明...」\n"
            "3. 需包含完整解题过程，示例：\n"
            "题目：已知函数f(x)=x³-3x\n"
            "(1) 求f(x)的极值点?\n"
            "(2) 证明该函数在区间[-2,2]上满足罗尔定理条件\n"
            "答案：\n"
            "(1) 导数为f'(x)=3x²-3，令f'(x)=0得x=±1...\n"
            "(2) 验证连续性、可导性及端点值相等..."
        ),
        "编程题": "需包含代码示例和测试用例"
    }

    return f"""【超严格指令】生成{num}道[{subject}]{question_type}（难度：{difficulty}）：
1. 返回严格JSON格式，包含question/answer/analysis
2. {type_rules.get(question_type, '')}
3. 示例：
{{
    "questions": [
        {{
            "question": "函数f(x)=x²的导数是？\\n选项：\\nA. 2x\\nB. x\\nC. 1\\nD. 0",
            "answer": "A",
            "analysis": "根据导数公式求得"
        }}
    ]
}}"""


def clean_json_content(content):
    """清洗API返回内容"""
    return content.replace('```json', '').replace('```', '').strip()


def validate_json(content):
    """验证JSON完整性"""
    try:
        json.loads(content)
        return True
    except:
        return False


def generate_questions(subject, difficulty, question_type, num):
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": build_prompt(subject, difficulty, question_type, num)}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 2000
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                headers=headers,
                json=data,
                timeout=40
            )

            if response.status_code != 200:
                print(f"[Attempt {attempt + 1}] HTTP Error {response.status_code}")
                continue

            content = response.json()['choices'][0]['message']['content']
            cleaned = clean_json_content(content)

            if not validate_json(cleaned):
                print(f"[Attempt {attempt + 1}] Invalid JSON")
                continue

            result = json.loads(cleaned)

            if question_type == "选择题":
                valid_questions = []
                for q in result.get('questions', []):
                    if 'A.' in q['question'] and 'B.' in q['question']:
                        valid_questions.append(q)
                    else:
                        print(f"过滤无效选择题：{q['question'][:50]}...")
                result['questions'] = valid_questions
                print(f"有效选择题数量：{len(valid_questions)}/{num}")

            return result

        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(3)

    return None


def save_results(data):
    """原有保存逻辑保持不变"""
    try:
        with open("output.txt", "w", encoding="utf-8") as f:
            for idx, q in enumerate(data['questions'], 1):
                question = q.get('question', '题目生成失败')
                answer = q.get('answer', '无答案')
                analysis = q.get('analysis', '无解析')

                f.write(f"【第{idx}题】{question}\n")
                f.write(f"答案：{answer}\n解析：{analysis}\n\n")
        return True
    except Exception as e:
        print(f"保存失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("试卷生成系统启动...")
    result = generate_questions("高等数学", "中等", "选择题", 3)
    if result:
        save_results(result)
        print("保存成功")
    else:
        print("生成失败")