# Website Modulues
from websites.Movizland import MovizLand
from websites.Shahid4u import Shahid4u
from websites.Cima4u import Cima4u
from websites.Mycima import MyCima

# Domains
MovizLand_domain = "movizland.date"
Shahid4u_domain = "shahed4u.rest"
Cima4u_domain = "cimaaa4u.online"
MyCima_domain = ""

# Site Objects
movizland = MovizLand(MovizLand_domain)
shahid4u = Shahid4u(Shahid4u_domain)
cima4u = Cima4u(Cima4u_domain)
mycima = MyCima(MyCima_domain)


def scrapingUrl(url):
    flag = True
    output = {}
    for website in (movizland, shahid4u, cima4u):
        if(website.domainName in url):
            print(website.domainName)
            website.setUrl(url)
            website.startScraping()
            output = website.getInformation()
            flag = False
            print(website.getInformation())
    if(flag):
        return -1
    return output


input_txt = input("Enter Movie Name or URL  >>  ")
output_dict = {}

if('http' in input_txt):  # URL
    output_dict = scrapingUrl(input_txt)
    if(output_dict == -1):
        print("Don't Accessed this type of URL")
else:  # Search by name
    for website in (movizland, shahid4u, cima4u):
        result = website.searchBy(input_txt)
        # from , videos
        videos = []
        print(result['from'])
        for idx in range(5):
            print(result['videos'][idx])
            videos.append(result['videos'][idx]['link'])
        print('')
    url_num = int(input("Choice Url number  >>  "))
    choice_url = videos[url_num]
    output_dict = scrapingUrl(choice_url)





## Error in MyCima Website