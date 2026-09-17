import requests

BACKEND_URL = "http://127.0.0.1:8001"

test_cases = [
    {"question": "How many orders are there in total?",                 "expected": "99441"},
    {"question": "How many customers are there?",                       "expected": "99441"},
    {"question": "Which product category generated the most revenue?",  "expected": "health_beauty"},
]

def evaluate(cases):
    passed = 0
    for case in cases:
        response = requests.post(f"{BACKEND_URL}/ask", json={"question": case["question"]})
        answer = response.json()["answer"]
        normalized = answer.lower().replace(",", "")          # "99,441" -> "99441"
        ok = case["expected"].lower() in normalized
        passed += ok
        print(f"{'✅ PASS' if ok else '❌ FAIL'} — {case['question']}")
        print(f"     expected: {case['expected']}  |  got: {answer[:70]}...")
    score = passed / len(cases) * 100
    print(f"\n===== SCORE: {passed}/{len(cases)} ({score:.0f}%) =====")

if __name__ == "__main__":
    evaluate(cases=test_cases)