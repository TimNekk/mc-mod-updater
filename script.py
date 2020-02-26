# noinspection PyBroadException

import zipfile
import re
import os
import googlesearch
import pickle
from colorama import init, Fore
from urllib import error
from bs4 import BeautifulSoup as BS
import cfscrape
import requests
import shutil

init()


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

        mod = {
            'name': re.findall(r'[\"][\w].+', re.findall(r'name.{4}[\w\s]+', file_data)[0])[0][1::],
            'file_name': file_name,
            'url': False
        }

        if mod['name'] in mods_exception:
            print(Fore.RED + mod['name'] + ' is not supported')
            return False

        try:
            mod['version'] = re.findall(r'[\w.-]+',
                                        re.findall(r'\"version.{4}[\w.-]+', file_data)[0][::-1])[0][::-1]
        except IndexError:
            print(Fore.RED + mod['name'] + ' - no "Version" found' + Fore.RESET)
            return False

        try:
            mod['mc_version'] = re.findall(r'[\"][\w].+',
                                           re.findall(r'mcversion.{4}[\w.-]+', file_data)[0])[0][1::]
        except IndexError:
            pass

        os.remove('mcmod.info')

        return mod
    else:
        print(Fore.RED + 'No "mcmod.info" found: ' + Fore.RESET)
        print(Fore.RED + file_path)
    return False


# def check_if_mod_in_mods_list(mod):
#     with open('mods.list', 'rb') as file:
#         mods_list = pickle.load(file)
#
#     try:
#         for mod_listed in mods_list:
#             if mod_listed['name'] == mod['name'] and mod_listed['version'] == mod['version']:
#                 print(Fore.CYAN +
#                       '{0} ({1}) is already up to date'.format(mod['name'], mod['version'])
#                       + Fore.RESET)
#                 return False
#
#     except TypeError:
#         print('Update_mod_info() - TypeError happened!')
#         reset_file('mods.list')
#
#     try:
#         for mod_listed in mods_list:
#             if mod_listed['name'] == mod['name']:
#                 mod['updated'] = True
#                 mod['url'] = False
#             print(Fore.GREEN +
#                   '{0} ({1}) added to "mods.list"'.format(mod['name'], mod['version'])
#                   + Fore.RESET)
#             return mod
#
#     except AttributeError:
#         print('Update_mod_info() - AttributeError happened!')
#         reset_file('mods.list')


def reset_file(file_name):
    with open(file_name, 'wb') as file:
        if file_name == 'mods.list':
            pickle.dump([], file)
        else:
            pickle.dump({}, file)
    print('------------------------------------------')
    print('"' + file_name + '" reset')
    print('------------------------------------------')


def show_mods_list(mode='everything'):
    print(Fore.BLUE + '\n"mods.list" content:' + Fore.RESET)
    with open('mods.list', 'rb') as file:
        mods_list = pickle.load(file)
        i = 0
        for mod in mods_list:
            if mode == 'everything':
                print('{0}) {1}'.format(i, mod))
            elif mode == 'name':
                print('{0}) {1}'.format(i, mod['name']))
            elif mode == 'version':
                print('{0}) {1}'.format(i, mod['version']))
            elif mode == 'updated':
                print('{0}) {1}'.format(i, mod['updated']))
            elif mode == 'url':
                print('{0}) {1}'.format(i, mod['url']))
            elif mode == 'mc_version':
                try:
                    print(str(i) + ') ' + mod['mc_version'])
                    print('{0}) {1}'.format(i, mod['mc_version']))
                except KeyError:
                    print('{0}) {1} has no "mc_version"'.format(i, mod['name']))
            i += 1
    print('\nTotal: {0} mods'.format(len(mods_list)))


def google(query):
    urls = []
    for url in googlesearch.search(query, tld="co.in", num=3, stop=3, pause=0):
        urls.append(url)
    return urls


def transform_files_urls(urls):
    new_urls = []
    for url in urls:
        new_url = re.findall(r'[\w\-:/.]+', url)[0]
        new_urls.append(new_url + '/files/all')
    return new_urls


def get_mod_url(mod_name, user_mc_version):
    urls = transform_files_urls(google('curseforge.com ' + mod_name))

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

                    mc_version = mc_version_container.select('.mr-2')[0].text
                    mc_version = re.findall(r'[\w.]+', mc_version)[0]
                    if mc_version == user_mc_version:
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
                            if mc_version == user_mc_version:
                                return url

            except IndexError:
                pass

        urls = transform_files_urls(google('curseforge.com ' + mod_name + 'updated'))
    return False


def update_mod_url(mod, user_mc_version):
    # print(Fore.BLUE + 'Mod url searching...')

    if not mod['url']:
        try:
            url = get_mod_url(mod['name'], user_mc_version)

            if url:
                mod['url'] = url
            else:
                mod['url'] = False
                print(Fore.RED +
                      '{0} ({1}) url not found!\n'.format(mod['name'], mod['version'])
                      + Fore.RESET)
        except error.HTTPError:
            print(Fore.RED + 'HTTP Error 429: Too Many Requests\n' + Fore.RESET)
            return False

        # print(Fore.GREEN +
        #       '{0} ({1}) url added:\n{2}\n'.format(mod['name'], mod['version'], mod['url'])
        #       + Fore.RESET)
        print(Fore.GREEN +
              'Url added: {0}'.format(mod['url'])
              + Fore.RESET)

        return mod


def check_if_mod_is_updated(mod, user_mc_version):

    scraper = cfscrape.create_scraper()

    try:
        r = scraper.get(mod['url'])
    except:
        return False

    soup = BS(r.content, 'html.parser')

    mod_versions = soup.select('.listing-container.listing-container-table:not(.custom-formatting) '
                               'table tbody tr')

    try:
        for row in mod_versions:
            mc_version_container = row.select('.listing-container.listing-container-table:'
                                              'not(.custom-formatting) table tbody tr td')[4]

            mc_version = mc_version_container.select('.mr-2')[0].text
            mc_version = re.findall(r'[\w.]+', mc_version)[0]

            if mc_version == user_mc_version:
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
                    if mc_version == user_mc_version:
                        top_row = row
                        raise Exception()

    except:
        pass

    version_container = top_row.select('.listing-container.listing-container-table:'
                                       'not(.custom-formatting) table tbody tr td')[1]

    new_version_text = version_container.select('a')[0].text
    if re.findall(r'[\d.]+', mod['version'])[0] in user_mc_version:
        try:
            mod['version'] = re.findall(r'[\d.]+', mod['version'])[1]
        except IndexError:
            mod['version'] = re.findall(r'[\d.]+', mod['version'])[0]
    else:
        mod['version'] = re.findall(r'[\d.]+', mod['version'])[0]

    if mod['version'] in new_version_text:  # Версию обновлять НЕ нужно
        mod['download_link'] = False

        print(Fore.GREEN +
              'Mod is up to date'
              + Fore.RESET)

        return mod

    else:  # Версию обновлять нужно
        old_mod_version = mod['version']
        old_mod_version = re.findall(r'[\d]+', old_mod_version)
        old_mod_version = ''.join(old_mod_version)

        edit_version = re.findall(r'[\d.]+', new_version_text)
        for new_version in edit_version:
            if user_mc_version in new_version or new_version == '.':
                continue

            if new_version[-1] == '.':
                new_version = new_version[:-1]

            new_version = re.findall(r'[\d]+', new_version)
            new_version = ''.join(new_version)

            break

        if int(new_version) > int(old_mod_version):

            download_link = version_container.select('a')[0].get('href')
            file_id = re.findall(r'files/[\d]+', download_link)[0]
            file_id = re.findall(r'[\d]+', file_id)[0]

            link_start = re.findall(r'.+files', download_link)[0][:-5]

            mod['download_link'] = 'https://www.curseforge.com' + link_start + 'download/' + file_id + '/file'
            mod['new_version_text'] = new_version_text

            edit_version = re.findall(r'[\d.]+', mod['new_version_text'])
            for new_version in edit_version:
                if mod['new_version_text'] in new_version or new_version == '.':
                    continue

                if new_version[-1] == '.':
                    new_version = new_version[:-1]

            mod['new_version'] = new_version

            print(Fore.RED +
                  'Mod can be updated ({0}) -> ({1})'.format(old_mod_version, new_version)
                  + Fore.RESET)

            return mod


def update_mod(mod, mods_dir, save_old_mod):
    if mod['download_link']:

        scraper = cfscrape.create_scraper()

        mod_file = False
        while not mod_file:
            mod_file = scraper.get(mod['download_link'])

        if not re.findall(r'.jar', mod['new_version_text']):
            mod['new_version_text'] += '.jar'

        with open(mod['new_version_text'], 'wb') as file:
            file.write(mod_file.content)

        if not os.path.exists(os.path.join(mods_dir, mod['new_version_text'])):
            shutil.move(mod['new_version_text'], mods_dir)

        if save_old_mod:
            if not os.path.isdir(mods_dir + '\\' + 'Old mods'):
                os.mkdir(mods_dir + '\\' + 'Old mods')

            if os.path.exists(mods_dir + '\\' + 'Old mods' + '\\' + mod['file_name']):
                os.remove(mods_dir + '\\' + 'Old mods' + '\\' + mod['file_name'])

            shutil.move(mods_dir + '\\' + mod['file_name'], mods_dir + '\\' + 'Old mods')

        else:
            os.remove(mods_dir + '\\' + mod['file_name'])

        print(Fore.GREEN +
              '{0} updated ({1}) -> ({2})'.format(mod['name'], mod['version'], mod['new_version'])
              + Fore.RESET)

    else:
        print(Fore.RED + '{0} is already updated!'.format(mod['name']) + Fore.RESET)

    return mod


def edit_user_mc_path(path):
    with open('user.settings', 'rb') as file:
        user_settings = pickle.load(file)

    user_settings['mc_path'] = path

    with open('user.settings', 'wb') as file:
        pickle.dump(user_settings, file)


def get_user_mc_path():
    with open('user.settings', 'rb') as file:
        try:
            return pickle.load(file)['mc_path']
        except:
            return False


def get_all_mc_versions():
    versions = []

    r = requests.get('https://minecraft.gamepedia.com/Java_Edition_version_history')
    soup = BS(r.content, 'html.parser')
    tables = soup.select('.wikitable')[1::]
    for table in tables:
        titles = table.select('a')

        for title in titles:
            if not re.findall(r'[A-z]', title.text):
                versions.append(title.text)
                if title.text == '1.0.0':
                    return versions


def delete_mod(mod, mods_dir):
    os.remove(os.path.join(mods_dir, mod['file_name']))


# def refresh(user_mc_version, mods_dir, reset=True):
#     if reset:
#         reset_file('mods.list')
#         reset_file('user.settings')
#
#     # while True:
#     #     try:
#     #         reset_mods_updated_status()
#     #         break
#     #     except FileNotFoundError:
#     #         print(Fore.RED + 'No "mods.list" found' + Fore.RESET)
#     #         reset_file('mods.list')
#
#     for file_name in os.listdir(mods_dir):
#         file_path = os.path.join(mods_dir, file_name)
#
#         if not os.path.isdir(file_path):
#             mod = get_mod_info(file_path, file_name)
#
#             print(mod['name'])
#
#             if mod:
#                 # updated_mod = update_mod_info(mod)
#                 # if updated_mod:
#                 #     mod = updated_mod
#
#                 mod = update_mod_url(mod, user_mc_version)
#                 mod = check_if_mod_is_updated(mod, user_mc_version)
#                 print()
#
#                 with open('mods.list', 'rb') as file:
#                     mods_list = pickle.load(file)
#
#                 mods_list.append(mod)
#
#                 with open('mods.list', 'wb') as file:
#                     pickle.dump(mods_list, file)

    # while True:
    #
    #     if not :
    #         show_mods_list()
    #         break
    # clear_mods_list()

# refresh('1.12.2', r'C:\Users\Tim PC\AppData\Roaming\.minecraft\mods', True)
#
# with open('mods.list', 'rb') as file:
#     listt = pickle.load(file)
#
# for mod in listt:
#     update_mod(mod, r'C:\Users\Tim PC\AppData\Roaming\.minecraft\mods', True)
#
# print(listt)