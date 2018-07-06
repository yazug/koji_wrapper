"""
Test the main KojiWrapper class
"""

import os

import koji
import pytest
from unittest.mock import MagicMock
from koji_wrapper.wrapper import KojiWrapper


sample_url = 'http://kojihub.com'
sample_topurl = 'http://somerepo.org'
sample_srpm_name = 'foo-bar-1.2-3.src.rpm'
sample_package_id = 12345
sample_package_name = 'foo-bar'
sample_tag_name = 'foo-tag'
sample_tag_id = 9999

sample_owner_name = 'jsmith'
sample_owner_id = 123

@pytest.fixture()
def sample_package_data():
    return {'id': sample_package_id, 'name': sample_package_name }


@pytest.fixture()
def sample_package_config_data():
    return {'owner_name': sample_owner_name, 'package_name': sample_package_name, 'extra_arches': None, 'package_id': sample_package_id, 'tag_id': sample_tag_id, 'tag_name': sample_tag_name, 'blocked': False, 'owner_id': sample_owner_id}


@pytest.fixture()
def a_koji_wrapper():
    return build_wrapper(None)


def build_wrapper(this_session):
    return KojiWrapper(url=sample_url,
                       topurl=sample_topurl,
                       session=this_session)


def test_set_init_values():
    """
    GIVEN KojiWrapper initialized with no session
    WHEN the object is created
    THEN session is set to an instance of koji.ClientSession
    AND we should have properly set url and topurl
    """
    test_wrapper = build_wrapper(None)
    assert test_wrapper.url == sample_url
    assert test_wrapper.topurl == sample_topurl
    assert isinstance(test_wrapper.session, koji.ClientSession)


def test_init_with_koji_client_session():
    """
    GIVEN we have a valid koji.ClientSession object,
    WHEN this object is passed as the session to a new KojiWrapper
    THEN this object's session is set to the session of the passed object
    """
    client_session = MagicMock(spec=koji.ClientSession)
    test_wrapper = build_wrapper(client_session)
    assert isinstance(test_wrapper.session, koji.ClientSession)


def test_init_with_koji_wrapper():
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN a KojiWrapper object is passed as the session to a new KojiWrapper
    THEN this object's session is set to the session of the passed object
    """
    my_koji_wrapper = build_wrapper(None)
    test_wrapper = build_wrapper(my_koji_wrapper)
    assert isinstance(test_wrapper.session, koji.ClientSession)
    assert test_wrapper.session is my_koji_wrapper.session


def test_init_with_koji_wrapper_only():
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN a KojiWrapper object is passed as the session to a new KojiWrapper
    THEN this object's session is set to the session and url/topurl
    """
    my_koji_wrapper = build_wrapper(None)
    test_wrapper = KojiWrapper(session=my_koji_wrapper)
    assert isinstance(test_wrapper.session, koji.ClientSession)
    assert test_wrapper.session is my_koji_wrapper.session
    assert test_wrapper.url is my_koji_wrapper.url
    assert test_wrapper.topurl is my_koji_wrapper.topurl


def test_gets_build(a_koji_wrapper, sample_build):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the build method with a valid nvr,
    THEN we get a build object back from the koji api
    """
    a_koji_wrapper.session.getBuild = MagicMock(return_value=sample_build)
    b = a_koji_wrapper.build('some_nvr')
    assert a_koji_wrapper.session.getBuild.called
    assert isinstance(b, dict)
    assert 'id' in b


def test_gets_rpms(a_koji_wrapper, sample_rpm_list):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the rpms method with a valid build_id,
    THEN we get a list of rpms back from the koji api
    """
    a_koji_wrapper.session.listRPMs = MagicMock(return_value=sample_rpm_list)
    rpms = a_koji_wrapper.rpms(buildID='some_nvr')
    assert a_koji_wrapper.session.listRPMs.called
    assert isinstance(rpms, list)
    ids = [i['build_id'] for i in rpms]
    assert 670920 in ids


def test_gets_archives(a_koji_wrapper, sample_archives):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the archives method with a valid build id and type,
    THEN we get a list of achives back from the koji api
    """
    a_koji_wrapper.session.listArchives = \
        MagicMock(return_value=sample_archives)
    arc = a_koji_wrapper.archives(buildID='12345', type='image')
    assert a_koji_wrapper.session.listArchives.called
    assert isinstance(arc, list)


def test_returns_file_types(a_koji_wrapper, sample_archives):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the archives method with a valid build id and type,
    THEN we get a list of file_types in the archive for the given nvr
    """
    a_koji_wrapper.session.listArchives = \
        MagicMock(return_value=sample_archives)
    a_koji_wrapper.session.getBuild = MagicMock(return_value={'id': '12345'})
    ft = a_koji_wrapper.file_types('myproject-9.0-20190326.1.el7')
    assert a_koji_wrapper.session.getBuild.called
    assert a_koji_wrapper.session.listArchives.called
    assert isinstance(ft, list)
    assert 'image' in ft


def test_returns_srpm_url(a_koji_wrapper, sample_build, sample_rpm_list):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the srpm_url method with a valid nvr,
    THEN we get a string representation of the srpm url for the given nvr
    """
    a_koji_wrapper.build = \
        MagicMock(return_value=sample_build)
    a_koji_wrapper.rpms = MagicMock(return_value=sample_rpm_list)
    a_koji_wrapper._build_srpm_url = \
        MagicMock(return_value='http://my.kojiserver/rpms/something.src.rpm')
    srpm_url = a_koji_wrapper.srpm_url('myproject-9.0-20190326.1.el7')
    assert a_koji_wrapper.build.called
    assert a_koji_wrapper.rpms.called
    assert a_koji_wrapper._build_srpm_url.called
    assert isinstance(srpm_url, str)


@pytest.mark.parametrize("srpm_name,build", [
    (None, None),
    ('', None),
    ('', ''),
    (None, ''),
    ('', ''),
])
def test_build_srpm_url_none_and_empty(a_koji_wrapper, srpm_name, build):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call _build_srpm_url method with parameters provided
    THEN we get back a TypeError
    """

    with pytest.raises(TypeError):
        a_koji_wrapper._build_srpm_url(srpm_name, build)


@pytest.mark.parametrize("build", [
    (None),
    (''),
])
def test_build_srpm_url_sample_srpm_name_none_or_empty(a_koji_wrapper, build):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call _build_srpm_url method with parameters provided
    THEN we get back a TypeError
    """

    with pytest.raises(TypeError):
        a_koji_wrapper._build_srpm_url(sample_srpm_name, build)


@pytest.mark.parametrize("srpm_name", [
    (None),
    (''),
])
def test_build_srpm_url_half_data_none_or_empty(a_koji_wrapper,
                                                srpm_name,
                                                sample_build):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call _build_srpm_url method with parameters provided
    THEN we get back a TypeError
    """

    with pytest.raises(TypeError):
        a_koji_wrapper._build_srpm_url(srpm_name, sample_build)


def test_build_srpm_url_positive(a_koji_wrapper, sample_build, sample_srpm):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call _build_srpm_url method with good srpm and build
    THEN we get back a url for sample srpm
    """

    expected_full_url = os.path.join(sample_topurl, sample_srpm_name)

    a_koji_wrapper._pathinfo = MagicMock(koji.PathInfo)
    a_koji_wrapper._pathinfo.rpm = MagicMock(return_value=sample_srpm_name)
    a_koji_wrapper._pathinfo.build = MagicMock(return_value=sample_topurl)
    srpm_full_path = a_koji_wrapper._build_srpm_url(sample_srpm, sample_build)
    assert srpm_full_path == expected_full_url


def test_srpm_url_raises_exception(a_koji_wrapper,
                                   sample_build,
                                   sample_rpm_list):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN we call the srpm_url method with an invalid nvr,
    THEN we get an exception raised
    """
    a_koji_wrapper.build = \
        MagicMock(return_value=sample_build)
    a_koji_wrapper.rpms = MagicMock(return_value=sample_rpm_list)
    a_koji_wrapper._build_srpm_url = \
        MagicMock(side_effect=Exception('Boom!'))
    with pytest.raises(Exception):
        a_koji_wrapper.srpm_url('wrongo')


@pytest.mark.parametrize('name', [None, ''])
def test_base_package_bad(a_koji_wrapper, name):
    """
    GIVEN we have a valid KojiBase with a session,
    WHEN a we call KojiBase::package() with None
    THEN we get back TypeError
    """
    a_koji_wrapper.session.getPackage = \
        MagicMock(side_effect=koji.GenericError(
            "invalid type for id lookup: <type 'NoneType'>"))

    with pytest.raises(ValueError):
        a_koji_wrapper.package(name)


def test_base_package_sample_package_name(a_koji_wrapper, sample_package_data):
    """
    GIVEN we have a valid KojiBase with a session,
    WHEN a we call KojiBase::package() with name
    THEN we get back dictionary
    """
    a_koji_wrapper.session.getPackage = MagicMock(return_value=sample_package_data)
    b = a_koji_wrapper.package(sample_package_name)
    assert a_koji_wrapper.session.getPackage.called
    assert isinstance(b, dict)
    assert 'id' in b

def test_base_package_sample_package_id(a_koji_wrapper, sample_package_data):
    """
    GIVEN we have a valid KojiBase with a session,
    WHEN a we call KojiBase::package() with id
    THEN we get back dictionary
    """
    a_koji_wrapper.session.getPackage = MagicMock(return_value=sample_package_data)
    b = a_koji_wrapper.package(sample_package_id)
    assert a_koji_wrapper.session.getPackage.called
    assert isinstance(b, dict)
    assert 'id' in b

@pytest.mark.parametrize('tag', [None, ''])
@pytest.mark.parametrize('name', [None, ''])
def test_base_package_config_bad(a_koji_wrapper, tag, name):
    """
    GIVEN we have a valid KojiWrapper with a session,
    WHEN a we call KojiBase::package_config() with None
    THEN we get back TypeError
    """
    a_koji_wrapper.session.getPackageConfig = \
        MagicMock(side_effect=koji.GenericError(
            "invalid type for id lookup: <type 'NoneType'>"))

    with pytest.raises(ValueError):
        a_koji_wrapper.package_config(tag, name)


@pytest.mark.parametrize('tag', [sample_tag_name, sample_tag_id])
@pytest.mark.parametrize('name', [sample_package_id, sample_package_name])
def test_base_package_config_sample_package(a_koji_wrapper, sample_package_config_data, tag, name):
    """
    GIVEN we have a valid KojiBase with a session,
    WHEN a we call KojiBase::package() with id
    THEN we get back dictionary
    """
    a_koji_wrapper.session.getPackageConfig = MagicMock(return_value=sample_package_config_data)
    b = a_koji_wrapper.package_config(tag, name)
    assert a_koji_wrapper.session.getPackageConfig.called
    assert isinstance(b, dict)
    assert 'package_id' in b
