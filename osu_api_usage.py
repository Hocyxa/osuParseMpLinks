import requests
import json

debug = False

def parse_mplink():
    if not debug:
        print("Вставьте ссылку на матч")
        match_url = input()  # https://osu.ppy.sh/community/matches/111534249
        match_id = match_url.split("/")[-1]
    else:
        match_id = 111534249

    with open("secrets.json", "r") as file:
        secrets = json.loads(file.read())
    token = requests.post("https://osu.ppy.sh/oauth/token",
                          data="client_id={}&client_secret={}&grant_type=client_credentials&scope=public"
                          .format(secrets["client_id"], secrets["client_secret"]),
                          headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"})  #
    if token.status_code != 200:
        print("Программа не смогла обратиться к API osu, проверьте интернет соединение или настройки json файла")
        exit(-1)

    access_token = token.json()["access_token"]

    match_info_raw = requests.get("https://osu.ppy.sh/api/v2/matches/{}".format(match_id),
                                  headers={"Authorization": "Bearer {}".format(access_token)})
    if match_info_raw.status_code != 200:
        print("Неверная ссылка на матч :( ")
        exit(-1)
    match_info_json = match_info_raw.json()
    user_dict = dict()
    for user in match_info_json["users"]:
        user_dict[user["id"]] = {"username": user["username"], "score_sum": 0}

    maps_played = 0
    matchcost_etalon = 5 * (10**5)
    for event in match_info_json["events"]:
        if event['detail']['type'] == 'other':
            if len(event['game']['scores']) > 0:
                maps_played += 1
                for score in event['game']['scores']:
                    user_dict[score["user_id"]]["score_sum"] += score["score"]
    for user_id, user_dict_username in user_dict.items():
        user_dict_username["average_score"] = user_dict_username["score_sum"] / maps_played
    sorted_list_by_average = sorted(user_dict.items(), key=lambda item: item[1]["average_score"], reverse=True)
    print("Maps played: {}".format(maps_played))
    for item in sorted_list_by_average:
        print(f"avg.score: {item[1]['average_score']}, match_cost: {item[1]['average_score'] / matchcost_etalon},  "
              f"score sum: { item[1]['score_sum']}  by {item[1]['username']}, user id: {item[0]}")


def parse_scrim(warmups=0):
    if not debug:
        print("Вставьте ссылку на матч")
        match_url = input()  # https://osu.ppy.sh/community/matches/111534249
        match_id = match_url.split("/")[-1]
    else:
        match_id = 111534249

    with open("secrets.json", "r") as file:
        secrets = json.loads(file.read())
    token = requests.post("https://osu.ppy.sh/oauth/token",
                          data="client_id={}&client_secret={}&grant_type=client_credentials&scope=public"
                          .format(secrets["client_id"], secrets["client_secret"]),
                          headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"})  #
    if token.status_code != 200:
        print("Программа не смогла обратиться к API osu, проверьте интернет соединение или настройки json файла")
        exit(-1)

    access_token = token.json()["access_token"]

    match_info_raw = requests.get("https://osu.ppy.sh/api/v2/matches/{}".format(match_id),
                                  headers={"Authorization": "Bearer {}".format(access_token)})
    if match_info_raw.status_code != 200:
        print("Неверная ссылка на матч :( ")
        exit(-1)
    match_info_json = match_info_raw.json()
    user_dict = dict()
    for user in match_info_json["users"]:
        user_dict[user["id"]] = {"username": user["username"], "maps_won": 0}

    maps_played = 0
    # matchcost_etalon = 5 * (10**5)
    for event in match_info_json["events"]:
        if event['detail']['type'] == 'other':
            if len(event['game']['scores']) > 0:
                maps_played += 1
                sorted_scores = event['game']['scores']
                sorted_scores.sort(key=lambda x: x['score'], reverse=True)
                if len(sorted_scores) < 2:
                    continue
                player_won_map_id = sorted_scores[0]["user_id"]
                user_dict[player_won_map_id]["maps_won"] += 1
    print(user_dict)
    print("Maps played: {}".format(maps_played))
    final_result = sorted(user_dict.items(), key=lambda pair: pair[1]["maps_won"], reverse=True)
    if len(final_result) < 2:
        return None
    elif len(final_result) > 2:
        final_result = final_result[0:2]
    return json.dumps(final_result)
    """
    for user_id, user_dict_username in user_dict.items():
        user_dict_username["average_score"] = user_dict_username["score_sum"] / maps_played
    sorted_list_by_average = sorted(user_dict.items(), key=lambda item: item[1]["average_score"], reverse=True)
    
    for item in sorted_list_by_average:
        print(f"avg.score: {item[1]['average_score']}, match_cost: {item[1]['average_score'] / matchcost_etalon},  "
              f"score sum: { item[1]['score_sum']}  by {item[1]['username']}, user id: {item[0]}")
    """

def get_user_id_by_username(username):
    with open("secrets.json", "r") as file:
        secrets = json.loads(file.read())
    token = requests.post("https://osu.ppy.sh/oauth/token",
                          data="client_id={}&client_secret={}&grant_type=client_credentials&scope=public"
                          .format(secrets["client_id"], secrets["client_secret"]),
                          headers={"Accept": "application/json",
                                   "Content-Type": "application/x-www-form-urlencoded"})  #
    if token.status_code != 200:
        print("Программа не смогла обратиться к API osu, проверьте интернет соединение или настройки json файла")
        exit(-1)
    access_token = token.json()["access_token"]

    user_info_raw = requests.get("https://osu.ppy.sh/api/v2/users/{}/osu".format(username),
                                  headers={"Authorization": "Bearer {}".format(access_token)})
    if user_info_raw.status_code != 200:
        print("Неверный username :( ")
        exit(-1)

    user_info = user_info_raw.json()
    # print(user_info)
    return user_info['id']


if __name__ == "__main__":
    """
    with open("data_new.json", "r") as file:
        players = json.loads(file.read())
    for player in players:
        user_id = get_user_id_by_username(player["nickname"])
        player.update({"user_id": user_id})
    # print(players)
    with open('data_new.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
    """
    # get_user_by_username("Boriska")
    parse_mplink()
    # parse_scrim()
