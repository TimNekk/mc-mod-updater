import zipfile
import re
import os
import yandex_search
import pickle
from colorama import init, Fore
from urllib import error
from bs4 import BeautifulSoup as BS
import cfscrape
import requests
import shutil
import data
import pathlib
init()

# noinspection PyBroadException

mods_exception = ['VoxelMap']
yandex = yandex_search.Yandex(api_user='megamax00', api_key='03.907013875:1908728c0c5f64a885f21721a1f1f4ee')


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
            print_console(mod['name'] + ' is not supported')
            return False

        try:
            mod['version'] = re.findall(r'[\w.-]+',
                                        re.findall(r'\"version.{4}[\w.-]+', file_data)[0][::-1])[0][::-1]
        except IndexError:
            print_console(mod['name'] + ' - no "Version" found')
            return False

        try:
            mod['mc_version'] = re.findall(r'[\"][\w].+',
                                           re.findall(r'mcversion.{4}[\w.-]+', file_data)[0])[0][1::]
        except IndexError:
            pass

        os.remove('mcmod.info')

        return mod
    else:
        print_console('No "mcmod.info" found: ')
        print_console(file_path)
    return False


def reset_file(file_name):
    with open(file_name, 'wb') as file:
        if file_name == 'mods.list':
            pickle.dump([], file)
        else:
            pickle.dump({}, file)
    print_console('------------------------------------------')
    print_console('"' + file_name + '" reset')
    print_console('------------------------------------------')


def show_mods_list(mode, mods):
    print_console('\nMods list:\n')

    i = 0
    for mod in mods:
        if mode == 'everything':
            print_console(mod['name'])
            for item in mod:
                print_console('{0}) {1}'.format(i, mod))
        elif mode == 'name':
            print_console('{0}) {1}'.format(i, mod['name']))
        elif mode == 'version':
            print_console('{0}) {1}'.format(i, mod['version']))
        elif mode == 'updated':
            print_console('{0}) {1}'.format(i, mod['updated']))
        elif mode == 'url':
            print_console('{0}) {1}'.format(i, mod['url']))
        elif mode == 'mc_version':
            try:
                print_console(str(i) + ') ' + mod['mc_version'])
                print_console('{0}) {1}'.format(i, mod['mc_version']))
            except KeyError:
                print_console('{0}) {1} has no "mc_version"'.format(i, mod['name']))
        i += 1
    print_console('\nTotal: {0} mods'.format(len(mods)))


def search_with_yandex(query):
    urls = []
    for item in yandex.search(query).items:
        urls.append(item['url'])
        if len(urls) == 3:
            break
    return urls


def transform_files_urls(urls):
    new_urls = []
    for url in urls:
        new_url = re.findall(r'[\w\-:/.]+', url)[0]
        new_urls.append(new_url + '/files/all')
    return new_urls


def get_mod_url(mod_name, user_mc_version):
    urls = transform_files_urls(search_with_yandex('curseforge.com ' + mod_name))

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

        urls = transform_files_urls(search_with_yandex('curseforge.com ' + mod_name + 'updated'))
    return False


def update_mod_url(mod, user_mc_version):
    if not mod['url']:
        try:
            url = get_mod_url(mod['name'], user_mc_version)

            if url:
                mod['url'] = url
            else:
                mod['url'] = False
                print_console('{0} ({1}) url not found!\n'.format(mod['name'], mod['version']))
        except error.HTTPError:
            print_console('HTTP Error 429: Too Many Requests\n')
            return '429'

        print_console('Url added: {0}'.format(mod['url']))

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

        print_console('Mod is up to date')

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

            print_console(                  'Mod can be updated ({0}) -> ({1})'.format(mod['version'], new_version)
                )
            print(mod)
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

        print_console('{0} updated ({1}) -> ({2})'.format(mod['name'], mod['version'], mod['new_version']))

    else:
        print_console('{0} is already updated!'.format(mod['name']))

    return mod


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


def delete_mod(mod):
    os.remove(os.path.join(data.user_mc_path, mod['file_name']))
    print_console('{0} deleted!'.format(mod['name']))


def print_console(text):
    data.console_text += text + '\n'
    print(text)
