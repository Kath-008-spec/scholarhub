import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

try:
    from django.conf import settings as _dj_settings
    DJ_DEBUG = bool(getattr(_dj_settings, 'DEBUG', False))
except Exception:
    DJ_DEBUG = False


class AIServiceError(Exception):
    pass


def _get_client() -> OpenAI:
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        raise AIServiceError('OpenAI API key is not configured. Set OPENAI_API_KEY in your .env file.')
    return OpenAI(api_key=api_key)


def build_prompt(profile: Any, course: Any, num_questions: int = 10, difficulty: str = 'medium', textbook_text: Optional[str] = None, question_type: str = 'objective', time_limit: Optional[int] = None) -> str:
    context = {
        'faculty': profile.faculty.name if profile.faculty else '',
        'department': profile.department.name if profile.department else '',
        'level': profile.level,
        'semester': profile.semester,
        'course_title': course.title,
        'num_questions': num_questions,
        'difficulty': difficulty,
        'question_type': question_type,
    }
    if textbook_text:
        context['textbook_excerpt'] = textbook_text[:4000]
    if time_limit:
        context['time_limit_minutes'] = time_limit

    if question_type == 'theory':
        instruction = (
            'Generate a JSON array of short essay-style questions for university students. '
            'Each item must have: question (string), expected_answer (string), explanation (string). '
            'Return ONLY valid JSON.'
        )
    else:
        instruction = (
            'Generate a JSON array of multiple-choice questions for university students. '
            'Each question must have: question (string), options (object mapping A-D to option text), '
            'answer (one of A,B,C,D), explanation (string). Return ONLY valid JSON.'
        )

    return json.dumps({'instruction': instruction, 'context': context}, ensure_ascii=False)


def parse_ai_response(resp_json: Any, question_type: str = 'objective') -> List[Dict[str, Any]]:
    if isinstance(resp_json, dict) and 'questions' in resp_json:
        items = resp_json['questions']
    elif isinstance(resp_json, list):
        items = resp_json
    else:
        raise AIServiceError('Unexpected AI response format from the model.')

    parsed = []
    for q in items:
        if not isinstance(q, dict):
            continue
        if 'question' not in q:
            continue

        if question_type == 'theory':
            parsed.append({
                'question': str(q['question']).strip(),
                'expected_answer': str(q.get('expected_answer', '')).strip(),
                'explanation': str(q.get('explanation', '')).strip(),
            })
            continue

        if isinstance(q.get('options'), dict) and q.get('answer') in ('A', 'B', 'C', 'D'):
            if set(q['options'].keys()) != {'A', 'B', 'C', 'D'}:
                continue
            parsed.append({
                'question': str(q['question']).strip(),
                'options': {
                    'A': str(q['options']['A']).strip(),
                    'B': str(q['options']['B']).strip(),
                    'C': str(q['options']['C']).strip(),
                    'D': str(q['options']['D']).strip(),
                },
                'answer': q['answer'],
                'explanation': str(q.get('explanation', '')).strip(),
            })

    if not parsed:
        raise AIServiceError('The model did not return usable questions. Please try again later.')
    return parsed


def generate_questions(profile: Any, course: Any, num_questions: int = 10, difficulty: str = 'medium', textbook_text: Optional[str] = None, question_type: str = 'objective', time_limit: Optional[int] = None) -> List[Dict[str, Any]]:
    prompt = build_prompt(profile, course, num_questions, difficulty, textbook_text, question_type=question_type, time_limit=time_limit)
    try:
        client = _get_client()
        response = client.responses.create(
            model='gpt-4.1-mini',
            input=[
                {
                    'role': 'system',
                    'content': 'You are an expert university course examiner. Return only valid JSON and nothing else.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=0.2,
        )
        text = getattr(response, 'output_text', '') or ''
        if not text:
            raise AIServiceError('The model returned an empty response.')
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            try:
                parsed = json.loads(text.split('```json', 1)[-1].split('```', 1)[0].strip())
            except Exception as exc:
                raise AIServiceError('The model returned invalid JSON. Please try again.') from exc
    except AIServiceError:
        raise
    except Exception as exc:
        raise AIServiceError(f'AI request failed: {exc}') from exc

    return parse_ai_response(parsed, question_type=question_type)
