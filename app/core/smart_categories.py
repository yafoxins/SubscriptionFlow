import re
from typing import Optional, Dict, List

class SmartCategoryDetector:
    """Умный детектор категорий подписок по названию"""
    
    # Словари ключевых слов для каждой категории
    CATEGORY_KEYWORDS = {
        'streaming': [
            'netflix', 'disney', 'hulu', 'amazon prime', 'hbo', 'youtube', 'twitch',
            'apple tv', 'paramount', 'peacock', 'crunchyroll', 'funimation',
            'ivi', 'kinopoisk', 'okko', 'more.tv', 'premier', 'tvzavr', 'megogo',
            'stream', 'видео', 'фильм', 'сериал', 'кино', 'тв', 'tv', 'prime', 'plus'
        ],
        'software': [
            'adobe', 'microsoft', 'office', 'photoshop', 'illustrator', 'premiere',
            'figma', 'sketch', 'notion', 'slack', 'zoom', 'teams', 'dropbox', 'google',
            'yandex', 'vk', 'mail.ru', 'rambler', 'cursor', 'jetbrains', 'intellij',
            'software', 'программа', 'приложение', 'софт', 'cloud', 'drive', 'one'
        ],
        'music': [
            'spotify', 'apple music', 'youtube music', 'deezer', 'tidal', 'pandora',
            'soundcloud', 'amazon music', 'google play music', 'napster', 'qobuz',
            'yandex.music', 'yandex music', 'vk music', 'vk.music', 'zaycev', 'zaycev.net',
            'музыка', 'music', 'audio', 'плейлист', 'playlist', 'радио', 'radio'
        ],
        'gaming': [
            'xbox', 'playstation', 'nintendo', 'steam', 'epic', 'origin', 'uplay',
            'battle.net', 'gog', 'twitch prime', 'game pass', 'ps plus', 'xbox live',
            'wargaming', 'mail.ru games', 'vk games', 'yandex games', 'playground',
            'игра', 'game', 'gaming', 'игровой', 'gamer', 'esports', 'киберспорт'
        ],
        'education': [
            'coursera', 'udemy', 'skillshare', 'masterclass', 'khan academy', 'edx',
            'pluralsight', 'lynda', 'linkedin learning', 'duolingo', 'babbel', 'rosetta',
            'stepik', 'yandex.praktikum', 'yandex praktikum', 'skillbox', 'geekbrains',
            'netology', 'coursera', 'stepik', 'htmlacademy', 'html academy',
            'обучение', 'курс', 'course', 'education', 'study', 'учеба', 'школа'
        ],
        'fitness': [
            'peloton', 'fitbit', 'myfitnesspal', 'strava', 'nike training', 'adidas',
            'garmin', 'polar', 'suunto', 'whoop', 'apple fitness', 'google fit',
            'yandex.plus', 'yandex plus', 'vk fit', 'vk.fitness', 'fitness',
            'фитнес', 'спорт', 'fitness', 'workout', 'тренировка', 'здоровье', 'health'
        ],
        'news': [
            'new york times', 'washington post', 'wall street journal', 'the economist',
            'financial times', 'bloomberg', 'reuters', 'associated press', 'cnn', 'bbc',
            'yandex.news', 'yandex news', 'rbc', 'ria', 'tass', 'interfax', 'kommersant',
            'vedomosti', 'novaya gazeta', 'meduza', 'the bell', 'fontanka',
            'новости', 'news', 'газета', 'журнал', 'magazine', 'newspaper', 'media'
        ],
        'productivity': [
            'notion', 'evernote', 'onenote', 'roam research', 'obsidian', 'logseq',
            'todoist', 'things', 'omnifocus', 'ticktick', 'microsoft todo', 'wunderlist',
            'yandex.disk', 'yandex disk', 'yandex.workspace', 'yandex workspace',
            'vk work', 'vk.work', 'mail.ru cloud', 'rambler.cloud',
            'продуктивность', 'productivity', 'задача', 'task', 'планировщик', 'календарь'
        ],
        'security': [
            'nordvpn', 'expressvpn', 'protonvpn', 'surfshark', 'cyberghost', 'tunnelbear',
            'lastpass', '1password', 'bitwarden', 'dashlane', 'roboform', 'keeper',
            'kaspersky', 'dr.web', 'eset', 'avast', 'norton', 'mcafee',
            'vpn', 'безопасность', 'security', 'пароль', 'password', 'шифрование'
        ],
        'storage': [
            'dropbox', 'google drive', 'onedrive', 'icloud', 'mega', 'pcloud', 'sync',
            'box', 'amazon drive', 'backblaze', 'crashplan', 'carbonite', 'idrive',
            'yandex.disk', 'yandex disk', 'yandex.cloud', 'yandex cloud',
            'mail.ru cloud', 'rambler.cloud', 'vk cloud', 'selectel', 'timeweb',
            'хранилище', 'storage', 'backup', 'резервная копия', 'облако', 'cloud'
        ]
    }
    
    # Приоритеты категорий (более специфичные категории имеют больший вес)
    CATEGORY_PRIORITIES = {
        'streaming': 12,
        'software': 11,
        'music': 10,
        'gaming': 9,
        'education': 8,
        'fitness': 7,
        'news': 6,
        'productivity': 5,
        'security': 4,
        'storage': 3
    }
    
    @classmethod
    def detect_category(cls, name: str, description: Optional[str] = None) -> Optional[str]:
        """
        Определяет категорию подписки по названию и описанию
        
        Args:
            name: Название подписки
            description: Описание подписки (опционально)
            
        Returns:
            Категория или None если не удалось определить
        """
        # Нормализуем текст
        text = f"{name} {description or ''}".lower()
        
        # Удаляем специальные символы и лишние пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Считаем совпадения для каждой категории
        category_scores = {}
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Точное совпадение слова
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    score += 2
                # Частичное совпадение
                elif keyword in text:
                    score += 1
            
            if score > 0:
                # Умножаем на приоритет категории
                base_score = score * cls.CATEGORY_PRIORITIES.get(category, 1)
                
                # Дополнительный бонус для российских сервисов
                russian_keywords = ['yandex', 'vk', 'mail.ru', 'rambler', 'ivi', 'kinopoisk', 
                                  'okko', 'stepik', 'skillbox', 'geekbrains', 'netology']
                for russian_keyword in russian_keywords:
                    if russian_keyword in text:
                        base_score *= 1.5  # 50% бонус для российских сервисов
                        break
                
                category_scores[category] = base_score
        
        if not category_scores:
            return None
        
        # Возвращаем категорию с наивысшим баллом
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    @classmethod
    def get_category_info(cls, category: str) -> Dict[str, str]:
        """Возвращает информацию о категории"""
        category_names = {
            'streaming': 'Стриминг',
            'software': 'Программное обеспечение',
            'music': 'Музыка',
            'gaming': 'Игры',
            'education': 'Образование',
            'fitness': 'Фитнес',
            'news': 'Новости',
            'productivity': 'Продуктивность',
            'security': 'Безопасность',
            'storage': 'Хранилище'
        }
        
        category_icons = {
            'streaming': 'fas fa-film',
            'software': 'fas fa-laptop-code',
            'music': 'fas fa-music',
            'gaming': 'fas fa-gamepad',
            'education': 'fas fa-graduation-cap',
            'fitness': 'fas fa-dumbbell',
            'news': 'fas fa-newspaper',
            'productivity': 'fas fa-tasks',
            'security': 'fas fa-shield-alt',
            'storage': 'fas fa-cloud'
        }
        
        return {
            'name': category_names.get(category, 'Другое'),
            'icon': category_icons.get(category, 'fas fa-tag')
        }
    
    @classmethod
    def get_all_categories(cls) -> List[Dict[str, str]]:
        """Возвращает список всех доступных категорий"""
        categories = []
        for category in cls.CATEGORY_KEYWORDS.keys():
            info = cls.get_category_info(category)
            categories.append({
                'value': category,
                'name': info['name'],
                'icon': info['icon']
            })
        return categories 