def base_template():

    return {
            "version" : "2.0",
            "data"    : {
                            "msg"  : "HI",
                            "name" : "DoveKim",
                            "position" : "API Developer" 
                    }
        }


def sale_template(informations):

    data = []
    for info in informations['data'].values():

        _temp = dict()
        _temp['title'] = info['name']
        _temp['genre'] = info['genre']

        data.append(_temp)

    return {
            "version"  : "2.0",
            "template" : {
                        "outputs" : [
                            {
                                "listCard" : {
                                    "header" : {
                                        "title" : "steam"
                                    },
                                    "items" : data
                                }
                            }
                        ]                
                    }

            }