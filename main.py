import zipfile
import re
import os
import googlesearch
import pickle
from colorama import init, Fore
from urllib import error
from bs4 import BeautifulSoup as BS
import cfscrape
import shutil

init()

mods_dir = 'C:\\Users\\Tim PC\\AppData\\Roaming\\.minecraft\\mods'
mods_exception = ['VoxelMap']


def unzip(file_path):
    archive = zipfile.ZipFile(file_path, 'r')
    try:
        archive.extract('mcmod.info')
    except KeyError:
        return False
    return True


def get_mod_info(file_path, file_name):
    if unzip(file_path):
        with open('mcmod.info', 'rb') as file:
            file_data = str(file.read())

        mod_info = {
            'name': re.findall(r'[\"][\w].+', re.findall(r'name.{4}[\w\s]+', file_data)[0])[0][1::],
            'file_name': file_name
        }

        if mod_info['name'] in mods_exception:
            print(Fore.RED + mod_info['name'] + ' is not supported')
            return False

        try:
            mod_info['version'] = re.findall(r'[\w.-]+',
                                             re.findall(r'\"version.{4}[\w.-]+', file_data)[0][::-1])[0][::-1]
        except IndexError:
            print(Fore.RED + mod_info['name'] + ' - no "Version" found' + Fore.RESET)
            return False

        try:
            mod_info['mc_version'] = re.findall(r'[\"][\w].+',
                                                re.findall(r'mcversion.{4}[\w.-]+', file_data)[0])[0][1::]
        except IndexError:
            pass

        os.remove('mcmod.info')

        return mod_info
    else:
        print(Fore.RED + 'No "mcmod.info" found: ' + Fore.RESET)
        print(Fore.RED + file_path)
    return False


def update_mod_info(mod_info):
    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)

    try:
        for mod in mods_list:
            if mod['name'] == mod_info['name'] and mod['version'] == mod_info['version']:
                print(Fore.CYAN + mod_info['name'] + ' (' + mod_info['version'] + ')' + ' is already up to date' +
                      Fore.RESET)
                mod['updated'] = True
                with open('mods.list', 'wb') as file:
                    pickle.dump(mods_list, file)
                return True

    except TypeError:
        print('Update_mod_info() - TypeError happened!')
        reset_file('mods.list')

    try:
        mods_list.append(mod_info)

        for mod in mods_list:
            if mod['name'] == mod_info['name']:
                mod['updated'] = True
                mod['url'] = False
                with open('mods.list', 'wb') as file:
                    pickle.dump(mods_list, file)

        print(Fore.GREEN + mod_info['name'] + ' (' + mod_info['version'] + ')' + ' added to "mods.list"' +
              Fore.RESET)
        with open('mods.list', 'wb') as file:
            pickle.dump(mods_list, file)
    except AttributeError:
        print('Update_mod_info() - AttributeError happened!')
        reset_file('mods.list')


def reset_file(file_name):
    with open(file_name, 'wb') as file:
        if file_name == 'mods.list':
            pickle.dump([], file)
        else:
            pickle.dump({}, file)
    print('------------------------------------------')
    print('"' + file_name + '" reseted')
    print('------------------------------------------')


def show_mods_list(mode='everything'):
    print(Fore.BLUE + '"mods.list" content:' + Fore.RESET)
    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)
        i = 0
        for mod in mods_list:
            if mode == 'everything':
                print(str(i) + ') ' + str(mod))
            elif mode == 'name':
                print(str(i) + ') ' + mod['name'])
            elif mode == 'version':
                print(str(i) + ') ' + mod['version'])
            elif mode == 'updated':
                print(str(i) + ') ' + mod['updated'])
            elif mode == 'url':
                print(str(i) + ') ' + mod['url'])
            elif mode == 'mc_version':
                try:
                    print(str(i) + ') ' + mod['mc_version'])
                except KeyError:
                    print(str(i) + ') ' + mod['name'] + ' has no "mc_version"')
            i += 1
    print('\nTotal: ' + str(len(mods_list)) + ' mods')


def google(query):
    urls = []
    for url in googlesearch.search(query, tld="co.in", num=3, stop=3, pause=2):
        urls.append(url)
    return urls


def transform_files_urls(urls):
    new_urls = []
    for url in urls:
        new_url = re.findall(r'[\w\-:/.]+', url)[0]
        new_urls.append(new_url + '/files/all')
    return new_urls


def get_mod_url(mod_name):
    urls = transform_files_urls(google('curseforge.com ' + mod_name))

    with open('user.settings', 'rb') as file:
        user_settings = pickle.load(file)

    scraper = cfscrape.create_scraper()

    for _ in range(0, 2):
        for url in urls:
            r = scraper.get(url)
            soup = BS(r.content, 'html.parser')
            try:
                mod_versions = soup.select('.listing-container.listing-container-table:not(.custom-formatting) '
                                           'table tbody tr')
                for row in mod_versions:
                    mc_version_container = row.select('.listing-container.listing-container-table:'
                                                      'not(.custom-formatting) table tbody tr td')[4]

                    # TODO - Обработка forge
                    mc_version = mc_version_container.select('.mr-2')[0].text
                    mc_version = re.findall(r'[\w.]+', mc_version)[0]
                    if mc_version == user_settings['mc_version']:
                        return url

                    elif mc_version == 'Forge':
                        version_container = row.select('.listing-container.listing-container-table:'
                                                       'not(.custom-formatting) table tbody tr td')[1]

                        version = version_container.select('a')[0]
                        forge_url = 'https://www.curseforge.com/' + version.get('href')
                        r = scraper.get(forge_url)

                        soup = BS(r.content, 'html.parser')
                        container = soup.select('.border-gray--100')[1]
                        mc_versions = container.select('.px-1')

                        for mc_version in mc_versions:
                            mc_version = re.findall(r'[\w. ]+', mc_version.text)[0]
                            if mc_version == user_settings['mc_version']:
                                return url

            except IndexError:
                pass

        urls = transform_files_urls(google('curseforge.com ' + mod_name + 'updated'))
    return False


def reset_mods_updated_status():
    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)

    for mod in mods_list:
        mod['updated'] = False

    with open('mods.list', 'wb') as file:
        pickle.dump(mods_list, file)

    print(Fore.BLUE + "\nAll mods' updated statuses were reseted\n" + Fore.RESET)


def clear_mods_list():
    print(Fore.BLUE + '\nClearing mods list...' + Fore.RESET)

    clearing_done = False
    while not clearing_done:
        clearing_done = True

        with open('mods.list', 'rb') as file:
            mods_list = pickle.load(file)

        for mod in mods_list:
            if not mod['updated']:
                print(Fore.RED + mod['name'] + ' (' + mod['version'] + ')' + ' was removed from "mods.list"' +
                      Fore.RESET)
                mods_list.remove(mod)
                with open('mods.list', 'wb') as file:
                    pickle.dump(mods_list, file)
                clearing_done = False

    print(Fore.BLUE + 'Clearing done!\n' + Fore.RESET)


def update_mods_url(reset=False):
    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)

    for mod in mods_list:
        if not mod['url'] or reset:
            try:
                url = get_mod_url(mod['name'])
                if url:
                    mod['url'] = url
                else:
                    mod['url'] = 'url not found'
                    print(Fore.RED + mod['name'] + ' (' + mod['version'] + ')' + ' url not found!' + Fore.RESET)
            except error.HTTPError:
                print(Fore.RED + 'HTTP Error 429: Too Many Requests\n' + Fore.RESET)
                return False

            with open('mods.list', 'wb') as file:
                pickle.dump(mods_list, file)
            print(Fore.GREEN + mod['name'] + ' (' + mod['version'] + ')' + ' url added:' + Fore.RESET)
            print(mod['url'] + '\n')


def check_user_settings():
    with open('user.settings', 'rb') as file:
        user_settings = pickle.load(file)
    try:
        version = user_settings['mc_version']
        print('\nMinecraft version: ' + Fore.GREEN + version + Fore.RESET)
    except KeyError:
        user_settings['mc_version'] = input(Fore.CYAN + '\nEnter your Minecraft Version: ' + Fore.RESET)

        with open('user.settings', 'wb') as file:
            pickle.dump(user_settings, file)


def test():
    scraper = cfscrape.create_scraper()

    with open('user.settings', 'rb') as file:
        user_settings = pickle.load(file)

    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)

    skip_mods = 8

    for mod in mods_list:
        if skip_mods != 0:
            skip_mods -= 1
            continue

        r = scraper.get(mod['url'])
        soup = BS(r.content, 'html.parser')

        mod_versions = soup.select('.listing-container.listing-container-table:not(.custom-formatting) '
                                   'table tbody tr')

        try:
            for row in mod_versions:
                mc_version_container = row.select('.listing-container.listing-container-table:'
                                                  'not(.custom-formatting) table tbody tr td')[4]

                mc_version = mc_version_container.select('.mr-2')[0].text
                mc_version = re.findall(r'[\w.]+', mc_version)[0]

                if mc_version == user_settings['mc_version']:
                    top_row = row
                    raise Exception()

                elif mc_version == 'Forge':
                    version_container = row.select('.listing-container.listing-container-table:'
                                                   'not(.custom-formatting) table tbody tr td')[1]

                    version = version_container.select('a')[0]
                    forge_url = 'https://www.curseforge.com/' + version.get('href')
                    r = scraper.get(forge_url)

                    soup = BS(r.content, 'html.parser')
                    container = soup.select('.border-gray--100')[1]
                    mc_versions = container.select('.px-1')

                    for mc_version in mc_versions:
                        mc_version = re.findall(r'[\w. ]+', mc_version.text)[0]
                        if mc_version == user_settings['mc_version']:
                            top_row = row
                            raise Exception()

        except:
            pass

        version_container = top_row.select('.listing-container.listing-container-table:'
                                           'not(.custom-formatting) table tbody tr td')[1]

        version_text = version_container.select('a')[0].text
        mod['version'] = re.findall(r'[\d.]+', mod['version'])[0]

        if mod['version'] in version_text:
            print(Fore.GREEN + mod['name'] + ' (' + mod['version'] + ') | ' + version_text + Fore.RESET)
        else:
            mod['version'] = re.findall(r'[\d]+', mod['version'])
            mod['version'] = ''.join(mod['version'])

            edit_version = re.findall(r'[\d.]+', version_text)
            for version in edit_version:
                if user_settings['mc_version'] in version or version == '.':
                    continue

                if version[-1] == '.':
                    version = version[:-1]

                version = re.findall(r'[\d]+', version)
                version = ''.join(version)

                break

            if int(version) > int(mod['version']):
                download_container = top_row.select('.listing-container.listing-container-table:'
                                                   'not(.custom-formatting) table tbody tr td')[6]

                download_link = version_container.select('a')[0].get('href')
                file_id = re.findall(r'files\/[\d]+', download_link)[0]
                file_id = re.findall(r'[\d]+', file_id)[0]

                link_start = re.findall(r'.+files', download_link)[0][:-5]

                download_link = 'https://www.curseforge.com' + link_start + 'download/' + file_id + '/file'

                mod_file = scraper.get(download_link)

                mod_dir = mods_dir + '\\' + version_text
                print(version_text)
                if not re.findall(r'.jar', version_text):
                    version_text += '.jar'
                print(version_text)

                with open(version_text, 'wb') as file:
                    file.write(mod_file.content)

                shutil.move(version_text, mod_dir)
                os.remove(mods_dir + '\\' + mod['file_name'])

            print(Fore.RED + mod['name'] + ' (' + mod['version'] + ') | ' + version + Fore.RESET)
        print(mod['url'])
        print()


def update(reset=False):
    if reset:
        reset_file('mods.list')
        reset_file('user.settings')

    try:
        reset_mods_updated_status()
    except FileNotFoundError:
        print(Fore.RED + 'No "mcmod.info" found' + Fore.RESET)
        reset_file('mods.list')
        reset_mods_updated_status()

    for file in os.listdir(mods_dir):
        file_path = os.path.join(mods_dir, file)

        if not os.path.isdir(file_path):
            # print(file_path)
            mod_info = get_mod_info(file_path, file)

            if mod_info:
                update_mod_info(mod_info)

    check_user_settings()
    clear_mods_list()
    update_mods_url()


update()
test()
show_mods_list()
# update()

