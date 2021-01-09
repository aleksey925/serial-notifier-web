class BaseNotification:

    def _build_notification_msg(self, tv_show_name: str, season_number: int, episode_number: int):
        return f'{tv_show_name}: Сезон {season_number}, Серия {episode_number}'
