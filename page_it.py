import hjson

if __name__ == "__main__":
    pod_dict = open("buttons.hjson","r").read()
    pod_dict = hjson.loads(pod_dict)
    page_split = list(pod_dict["Pods"].items())
    start = 0
    finish = 6
    cards_size = (len(page_split))
    print(cards_size)
    page_num = 2
    if (page_num * 6) < cards_size:
        finish = page_num * 6
        if page_num > 1:
            start = (finish + 1)-6
        else:
            start = 0
    else:
        finish = cards_size
        start = ((page_num * 6)) - 6
    for key, value in page_split[start:finish]:
        print(value['label'])