from django.db import models

# Create your models here.
class SteamDB(models.Model):

    ## appid     : 스팀 상점에 있는 게임, DLC 등 app id (기본키로 사용)
    ## json_path : appid에 해당하는 정보를 담고 있는 json 파일 경로

    appid     = models.TextField(primary_key = True)
    json_path = models.TextField()

    def __str__(self): return f'steam app id : {self.appid}'

    
    def __len__(self): return len(self.appid)