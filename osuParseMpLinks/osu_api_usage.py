import requests
import json
import re

debug = False


def parse_mplink(match_arg=None, warmups=0, skip_last=0, verbose=True):
    """
    Parse a mp link and give information about avg_score
    :param match_arg:
        URL/ID to a match
    :param warmups:
        number of warmups (amount of maps that will be skipped from beginning)
    :param skip_last:
        amount of maps that
    :param verbose:
        will or will not the additional information be printed
    :return:
        scores_to_return : list - parsed scores (warmup and skip_last are filters applied)
            - "beatmap_id" : int
            - "scores": list of dicts for every score of a player. Main keys:
                - "score"
                - "user_id"
                - "mods"
                - "accuracy"
        user_dict: dict - user information. Key is an id of the player, values are:
            - "username"
            - "score_sum"
            - "average_score"
            - "played_maps": dict of beatmaps, that the player has played. Key is beatmap_id, values are:
                - "score"
                - "mods"
                - and so on
    """
    if not debug and not match_arg:
        print("Вставьте ссылку на матч")
        match_url = input()  # https://osu.ppy.sh/community/matches/111534249
    else:
        match_url = match_arg if match_arg else 111555364

    if '/' in match_url:
        match_id = re.findall('matches/\d+', match_url)
        if len(match_id) < 1:
            print("Неверная ссылка на матч!")
            return
        match_id = int(match_id[0].split('/')[1])  # example: 'matches/113456' -> 113456: int
    else:
        match_id = int(match_url)
    with open("secrets.json", "r") as file:
        secrets = json.loads(file.read())
    token = requests.post("https://osu.ppy.sh/oauth/token",
                          data="client_id={}&client_secret={}&grant_type=client_credentials&scope=public"
                          .format(secrets["client_id"], secrets["client_secret"]),
                          headers={"Accept": "application/json",
                                   "Content-Type": "application/x-www-form-urlencoded"})  #
    if token.status_code != 200:
        print("Программа не смогла обратиться к API osu, проверьте интернет соединение или настройки json файла")
        raise ValueError(
            "Программа не смогла обратиться к API osu, проверьте интернет соединение или настройки json файла")

    access_token = token.json()["access_token"]

    match_info_raw = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}",
                                  headers={"Authorization": f"Bearer {access_token}"})
    if match_info_raw.status_code != 200:
        print("Неверная ссылка на матч :( ")
        raise ValueError("Неверная ссылка на матч :(")
    match_info_json = match_info_raw.json()
    user_dict = dict()
    for user in match_info_json["users"]:
        user_id = user["id"]
        user_dict[user_id] = {"username": user["username"], "score_sum": 0, 'played_maps': {}}
    first_event_id = match_info_json['first_event_id']
    last_event_id = match_info_json['latest_event_id']
    event_id = first_event_id
    all_scores = []
    # парсинг всех ивентов
    while event_id < last_event_id:  # пока что так, но возможно это ошибка
        match_info_raw = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}?after={event_id}",
                                      headers={"Authorization": f"Bearer {access_token}"})
        match_info_json = match_info_raw.json()
        for user in match_info_json["users"]:
            user_id = user["id"]
            if user_id not in user_dict:
                user_dict[user_id] = {"username": user["username"], "score_sum": 0, 'played_maps': {}}
        event_id = match_info_json['events'][-1]['id']
        for event in match_info_json['events']:
            if event['detail']['type'] == 'other' and len(event['game']['scores']) > 0:
                scores_struct = event['game']['scores']
                scores_struct = {"scores": scores_struct, "beatmap_id": event['game']['beatmap_id']}
                all_scores.append(scores_struct)
    # обработка полученных результатов + warmup/skip_last
    parsed = 0
    to_parse = len(all_scores)
    scores_to_return = []
    for score_struct in all_scores:
        parsed += 1
        if parsed > to_parse - skip_last:
            break
        if warmups > 0:
            warmups -= 1
            continue
        scores_to_return.append(score_struct)
        beatmap_id = score_struct['beatmap_id']
        scores = score_struct['scores']
        for score in scores:
            user_id = score["user_id"]
            if beatmap_id in user_dict[user_id]["played_maps"]:  # if a player has played the map twice or more
                old_score = user_dict[user_id]["played_maps"][beatmap_id]['score']
                if old_score <= score['score']:
                    user_dict[user_id]["played_maps"][beatmap_id] = score
            else:
                user_dict[user_id]["played_maps"].update({beatmap_id: score})

    matchcost_etalon = 5 * (10 ** 5)  # 500k
    for user_id, user_dict_username in user_dict.items():
        maps_played = 0
        user_played_maps = user_dict_username['played_maps']
        user_dict_username['score_sum'] = 0
        for map_id, score_struct in user_played_maps.items():
            maps_played += 1
            user_dict_username['score_sum'] += score_struct['score']
        if len(user_dict_username["played_maps"]) > 0:
            user_dict_username["average_score"] = user_dict_username["score_sum"] / len(user_dict_username["played_maps"])
        else:
            user_dict_username["average_score"] = 0
    sorted_list_by_average = sorted(user_dict.items(), key=lambda item: item[1]["average_score"], reverse=True)
    if verbose:
        for user_id, user_details in sorted_list_by_average:
            print(f"avg.score: {user_details['average_score']}, "
                  f"match_cost: {user_details['average_score'] / matchcost_etalon}, "
                  f"played maps: {len(user_details['played_maps'])} "
                  f"score sum: {user_details['score_sum']}  by {user_details['username']}, user id: {user_id}")
    return scores_to_return, user_dict


def parse_scrim(match_arg=None, warmups=0, skip_last=0, verbose=True):
    """
    Parse a scrim (1vs1) match, using the parse_mplink function
    :param match_arg:
        URL/ID to a match
    :param warmups:
        number of warmups (amount of maps that will be skipped from beginning)
    :param skip_last:
        amount of maps that
    :param verbose:
        will or will not the additional information be printed
    :return:
        final_result: list (in json format).
        It consists of performance by two best players (if the number of players > 2).
        If the number of players < 2, returns None
            - index 0 (player that won) : tuple
                - user_id
                - user_info: dict
                    - "maps_won"
                    - "average_score"
                    - ...
            - index 1 (player that lose or tied): tuple - structure is the same as index 0
    """
    if not debug and not match_arg:
        print("Вставьте ссылку на матч")
        match_url = input()  # https://osu.ppy.sh/community/matches/111534249
        match_id = match_url.split("/")[-1]
    else:
        match_id = match_arg if match_arg else 111534249

    scores_info, user_dict = parse_mplink(match_id, warmups, skip_last, verbose=False)
    for user_id, user_info in user_dict.items():
        user_dict[user_id].update({"maps_won": 0})

    maps_played = len(scores_info)
    for score_info in scores_info:  # score: {"beatmap_id": ..., "scores": [...]}
        scores = score_info['scores']
        scores.sort(key=lambda x: x['score'], reverse=True)
        if len(scores) < 2:
            continue
        player_won_map_id = scores[0]['user_id']
        user_dict[player_won_map_id]['maps_won'] += 1

    if verbose:
        print(user_dict)
        print("Maps played: {}".format(maps_played))
    final_result = sorted(user_dict.items(), key=lambda pair: pair[1]["maps_won"], reverse=True)
    if len(final_result) < 2:
        return None
    elif len(final_result) > 2:
        final_result = final_result[0:2]
    return json.dumps(final_result)


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
    parse_mplink(warmups=0, skip_last=0)

    """matches = ["https://osu.ppy.sh/community/matches/114155474", "https://osu.ppy.sh/community/matches/114155177",
               "https://osu.ppy.sh/community/matches/114131550", "https://osu.ppy.sh/community/matches/113799771",
               "https://osu.ppy.sh/community/matches/113690530", "https://osu.ppy.sh/community/matches/113343257",
               "https://osu.ppy.sh/community/matches/113101878", "https://osu.ppy.sh/community/matches/113069141",
               "https://osu.ppy.sh/community/matches/112981168"]
    for match in matches:
        result = json.loads(parse_scrim(match_arg=match, verbose=False))
        print(f"{result[0][1]['username']} {result[0][1]['maps_won']} - {result[1][1]['maps_won']} "
              f"{result[1][1]['username']}")"""
