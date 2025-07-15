import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from app.models.subscription import Subscription

class CalendarIntegration:
    """Интеграция с календарями (Google Calendar, Outlook)"""
    
    # Google Calendar API настройки
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar']
    GOOGLE_TOKEN_FILE = 'google_calendar_token.json'
    GOOGLE_CREDENTIALS_FILE = 'google_calendar_credentials.json'
    
    def __init__(self):
        self.google_service = None
        self.outlook_token = None
    
    # Google Calendar методы
    def setup_google_calendar(self, credentials_json: str) -> Dict[str, Any]:
        """Настройка Google Calendar интеграции"""
        try:
            # Сохраняем credentials
            with open(self.GOOGLE_CREDENTIALS_FILE, 'w') as f:
                f.write(credentials_json)
            
            # Получаем токен
            flow = InstalledAppFlow.from_client_secrets_file(
                self.GOOGLE_CREDENTIALS_FILE, self.GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Сохраняем токен
            with open(self.GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            self.google_service = build('calendar', 'v3', credentials=creds)
            
            return {
                'success': True,
                'message': 'Google Calendar успешно подключен'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка подключения к Google Calendar: {str(e)}'
            }
    
    def _get_google_credentials(self) -> Optional[Credentials]:
        """Получение Google credentials"""
        creds = None
        
        if os.path.exists(self.GOOGLE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(
                self.GOOGLE_TOKEN_FILE, self.GOOGLE_SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                return None
        
        return creds
    
    def add_subscription_to_google_calendar(self, subscription: Subscription) -> Dict[str, Any]:
        """Добавление подписки в Google Calendar"""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return {
                    'success': False,
                    'message': 'Не удалось получить доступ к Google Calendar'
                }
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Создаем событие
            event = {
                'summary': f'💳 {subscription.name} - {subscription.price} {subscription.currency}',
                'description': f'Подписка: {subscription.name}\n'
                             f'Цена: {subscription.price} {subscription.currency}\n'
                             f'Цикл: {subscription.billing_cycle}\n'
                             f'Категория: {subscription.category or "Не указана"}',
                'start': {
                    'dateTime': subscription.next_billing_date.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': (subscription.next_billing_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # За день
                        {'method': 'popup', 'minutes': 60},  # За час
                    ],
                },
                'colorId': self._get_color_id_for_category(subscription.category),
            }
            
            event = service.events().insert(
                calendarId='primary',
                body=event,
                recurringEventId=None
            ).execute()
            
            return {
                'success': True,
                'message': 'Подписка добавлена в Google Calendar',
                'event_id': event['id']
            }
            
        except HttpError as error:
            return {
                'success': False,
                'message': f'Ошибка Google Calendar API: {error}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка добавления в Google Calendar: {str(e)}'
            }
    
    def _get_color_id_for_category(self, category: Optional[str]) -> str:
        """Получение цвета события по категории"""
        color_map = {
            'streaming': '1',      # Красный
            'software': '2',       # Оранжевый
            'music': '3',          # Желтый
            'gaming': '4',         # Зеленый
            'education': '5',      # Голубой
            'fitness': '6',        # Синий
            'news': '7',           # Фиолетовый
            'productivity': '8',   # Розовый
            'security': '9',       # Серый
            'storage': '10',       # Темно-серый
        }
        return color_map.get(category, '11')  # По умолчанию белый
    
    def update_subscription_in_google_calendar(self, subscription: Subscription, event_id: str) -> Dict[str, Any]:
        """Обновление события подписки в Google Calendar"""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return {
                    'success': False,
                    'message': 'Не удалось получить доступ к Google Calendar'
                }
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Обновляем событие
            event = {
                'summary': f'💳 {subscription.name} - {subscription.price} {subscription.currency}',
                'description': f'Подписка: {subscription.name}\n'
                             f'Цена: {subscription.price} {subscription.currency}\n'
                             f'Цикл: {subscription.billing_cycle}\n'
                             f'Категория: {subscription.category or "Не указана"}',
                'start': {
                    'dateTime': subscription.next_billing_date.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': (subscription.next_billing_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'colorId': self._get_color_id_for_category(subscription.category),
            }
            
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'message': 'Событие обновлено в Google Calendar'
            }
            
        except HttpError as error:
            return {
                'success': False,
                'message': f'Ошибка Google Calendar API: {error}'
            }
    
    def delete_subscription_from_google_calendar(self, event_id: str) -> Dict[str, Any]:
        """Удаление события подписки из Google Calendar"""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return {
                    'success': False,
                    'message': 'Не удалось получить доступ к Google Calendar'
                }
            
            service = build('calendar', 'v3', credentials=creds)
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': 'Событие удалено из Google Calendar'
            }
            
        except HttpError as error:
            return {
                'success': False,
                'message': f'Ошибка Google Calendar API: {error}'
            }
    
    # Outlook методы
    def setup_outlook_calendar(self, access_token: str) -> Dict[str, Any]:
        """Настройка Outlook интеграции"""
        try:
            self.outlook_token = access_token
            
            # Проверяем доступ к API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/calendarView',
                headers=headers,
                params={'top': 1}
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Outlook Calendar успешно подключен'
                }
            else:
                return {
                    'success': False,
                    'message': 'Не удалось подключиться к Outlook Calendar'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка подключения к Outlook: {str(e)}'
            }
    
    def add_subscription_to_outlook_calendar(self, subscription: Subscription) -> Dict[str, Any]:
        """Добавление подписки в Outlook Calendar"""
        try:
            if not self.outlook_token:
                return {
                    'success': False,
                    'message': 'Outlook не подключен'
                }
            
            headers = {
                'Authorization': f'Bearer {self.outlook_token}',
                'Content-Type': 'application/json'
            }
            
            event = {
                'subject': f'💳 {subscription.name} - {subscription.price} {subscription.currency}',
                'body': {
                    'contentType': 'text',
                    'content': f'Подписка: {subscription.name}\n'
                              f'Цена: {subscription.price} {subscription.currency}\n'
                              f'Цикл: {subscription.billing_cycle}\n'
                              f'Категория: {subscription.category or "Не указана"}'
                },
                'start': {
                    'dateTime': subscription.next_billing_date.isoformat(),
                    'timeZone': 'Europe/Moscow'
                },
                'end': {
                    'dateTime': (subscription.next_billing_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Europe/Moscow'
                },
                'reminderMinutesBeforeStart': 60,
                'isReminderOn': True
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                json=event
            )
            
            if response.status_code == 201:
                event_data = response.json()
                return {
                    'success': True,
                    'message': 'Подписка добавлена в Outlook Calendar',
                    'event_id': event_data['id']
                }
            else:
                return {
                    'success': False,
                    'message': f'Ошибка добавления в Outlook: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка добавления в Outlook: {str(e)}'
            }
    
    def get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Получение событий из календарей"""
        events = []
        
        # Google Calendar события
        try:
            creds = self._get_google_credentials()
            if creds:
                service = build('calendar', 'v3', credentials=creds)
                
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=start_date.isoformat() + 'Z',
                    timeMax=end_date.isoformat() + 'Z',
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                for event in events_result.get('items', []):
                    events.append({
                        'source': 'google',
                        'id': event['id'],
                        'title': event['summary'],
                        'description': event.get('description', ''),
                        'start': event['start'].get('dateTime'),
                        'end': event['end'].get('dateTime'),
                        'color': event.get('colorId', '11')
                    })
        except Exception:
            pass
        
        # Outlook события
        try:
            if self.outlook_token:
                headers = {
                    'Authorization': f'Bearer {self.outlook_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    'https://graph.microsoft.com/v1.0/me/calendarView',
                    headers=headers,
                    params={
                        'startDateTime': start_date.isoformat(),
                        'endDateTime': end_date.isoformat()
                    }
                )
                
                if response.status_code == 200:
                    outlook_events = response.json().get('value', [])
                    for event in outlook_events:
                        events.append({
                            'source': 'outlook',
                            'id': event['id'],
                            'title': event['subject'],
                            'description': event.get('bodyPreview', ''),
                            'start': event['start']['dateTime'],
                            'end': event['end']['dateTime']
                        })
        except Exception:
            pass
        
        return events 