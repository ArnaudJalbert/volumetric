import os.path
import unittest
from unittest import mock
from database.testing import MockedDatabaseTest
from deliver.deliver_type import DeliveryType
from deliver.data_model import DeliveryDataModel
from deliver.delivery.image_delivery import ImageDelivery
from deliver.core import CreateDeliveries
from entities.delivery_config import DeliveryConfig
from entities.playlist import Playlist
from entities.version import Version
from oreo_cream.publish_types import PublishTypes
from oreo_cream.crumbs.oreo_cream_stockitems.delivery_media_items import (
    DeliveryMovieItem,
    DeliveryImageSequenceItem,
)
import inspect


class DeliveryTests(MockedDatabaseTest):
    _created_entities = []

    def setUp(self):
        self.db = self.mocked_database()

        self.fake_project = self.create_test_project()
        self._created_entities.append(self.fake_project)

        self.fake_user = self.create_test_user("mon_user")
        self._created_entities.append(self.fake_user)

        self.fake_sequence = self.create_test_sequence(self.fake_project)
        self._created_entities.append(self.fake_sequence)

        self.fake_shot = self.create_test_shot(self.fake_sequence)
        self._created_entities.append(self.fake_shot)

        self.fake_task = self.create_test_task(self.fake_shot)
        self._created_entities.append(self.fake_task)

        self.fake_playlist = self._create_fake_playlist()

        self.fake_delivery_config = self._create_fake_delivery_config()

        self.fake_version = self._creater_fake_version()
        self.fake_version.task = self.fake_task

    def tearDown(self):
        for e in self._created_entities:
            self.db.delete(e)

    def _create_fake_playlist(self, code="SuperPlaylist"):
        playlist = Playlist()
        playlist.code = code
        playlist = self.db.create_playlist(playlist, self.fake_project.id)
        self._created_entities.append(playlist)
        return playlist

    def test_deliver_version_data_model_has_published_file_nuke_script_not_exists(self):
        data_model = DeliveryDataModel(
            self.db,
            self.fake_project.name,
            self.fake_playlist.id,
            [self.fake_version.id],
        )
        self.assertListEqual(
            data_model.nuke_script_by_version_id[self.fake_version.id], []
        )

    def test_deliver_version_data_model_has_published_file_nuke_script(self):
        # Nuke script published file
        nuke_script = "super_nuke_script.nk"
        published_file_type = self.create_test_published_file_type(
            PublishTypes.NUKE_SCENE.value
        )
        nuke_script_published_file = self.create_test_published_file(
            self.fake_shot, published_file_type, filepath=nuke_script
        )
        self._created_entities.append(nuke_script_published_file)

        # ImageSequence Published file
        published_type = self.create_test_published_file_type(
            PublishTypes.RENDER_IMAGES.value
        )
        image_sequence_published_file = self.create_test_published_file(
            self.fake_shot, published_type
        )
        image_sequence_published_file.version = self.fake_version
        image_sequence_published_file.work_file_link = nuke_script_published_file
        self.db.update_entity(
            image_sequence_published_file, ["version", "work_file_link"]
        )
        self._created_entities.append(image_sequence_published_file)

        data_model = DeliveryDataModel(
            self.db,
            self.fake_project.name,
            self.fake_playlist.id,
            [self.fake_version.id],
        )

        self.assertEqual(
            nuke_script, data_model.nuke_script_by_version_id[self.fake_version.id][0]
        )

    def _creater_fake_version(self):
        """

        Returns:
            Version:
        """
        version = Version()
        version.code = "super_version"
        version.link = self.fake_shot
        version.project = self.fake_project
        version.created_by = self.fake_user
        version.path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "COOL_FAKE_DELIVERY_20230602",
            "TEST_008_050_COMP_v007",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.first_frame = 1001
        version.last_frame = 1005
        version = self.db.create_version(version)
        self._created_entities.append(version)
        return version

    def _create_fake_delivery_config(
        self,
        _type=DeliveryType.OFFLINE,
        code="super_code",
        template="{Project.name}/{Shot.code}",
    ):
        dc = DeliveryConfig()
        dc.code = code
        dc.delivery_type = _type.value
        dc.name_template = template
        self.db.create_entity(dc, ["delivery_type", "name_template"])
        self._created_entities.append(dc)
        return dc

    def test_create_delivery_space_in_playlist_code(self):
        playlist = self._create_fake_playlist(code="AName With Space")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = CreateDeliveries(
            data_model, test_mode=None, enforce_type_list=None
        )
        self.assertFalse(create_deliveries.is_valid())
        self.assertFalse(create_deliveries.can_be_processed())
        self.assertListEqual(
            create_deliveries.errors, ["Please remove spaces in the playlist name"]
        )

    def test_all_frames_continuous(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_missing_frame_1003",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1007
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        errors = set(create_deliveries.errors)  # remove duplicates
        self.assertSetEqual(
            errors,
            {
                "Missing frame(s) between frames 1003 and 1005 of version {0} (Path: {1}).".format(
                    version.code, path_to_frames
                )
            },
        )

    def test_first_frame_missing(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_missing_first_frame",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1005
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        errors = set(create_deliveries.errors)  # remove duplicates
        self.assertSetEqual(
            errors,
            {
                "Missing the first frame 1001 of version {0} (Path: {1}.)".format(
                    version.code, path_to_frames
                )
            },
        )

    def test_last_frame_missing(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_missing_last_frame",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1005
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        errors = set(create_deliveries.errors)  # remove duplicates
        self.assertSetEqual(
            errors,
            {
                "Missing the last frame 1005 of version {0} (Path: {1}.)".format(
                    version.code, path_to_frames
                )
            },
        )

    def test_no_frames_in_directory(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_no_frames",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1005
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        errors = set(create_deliveries.errors)  # remove duplicates
        self.assertSetEqual(
            errors,
            {"There is not a valid frame sequence at path {0}".format(path_to_frames)},
        )

    def test_no_directory(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_no_dir",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1005
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        errors = set(create_deliveries.errors)  # remove duplicates
        self.assertSetEqual(
            errors, {'Path to frame is missing" {}'.format(path_to_frames)}
        )

    def test_one_frame_in_path_to_frames(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_one_frame",
            "TEST_008_050_COMP_v007.####.exr",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1003
        version.last_frame = 1003
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        self.assertEqual(len(create_deliveries.errors), 0)

    def test_one_frame_in_path_to_frames_no_padding(self):
        playlist = self._create_fake_playlist(code="frames_not_continuous")

        dc = self._create_fake_delivery_config()

        version = self._creater_fake_version()
        version.delivery_formats = [dc]
        path_to_frames = os.path.join(
            os.path.dirname(inspect.getfile(inspect.currentframe())),
            "test_data",
            "path_to_frames",
            "TEST_008_050_COMP_v007_one_frame_no_pad",
            "TEST_008_050_concept_ajalbert.jpg",
        )
        version.path_to_frames = path_to_frames
        version.first_frame = 1001
        version.last_frame = 1001
        self.db.update_entity(version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db, self.fake_project.name, playlist.id, [version.id]
        )

        create_deliveries = ImageDelivery(dc, version, data_model)
        create_deliveries._sanity_check()
        print(create_deliveries.errors)
        self.assertEqual(len(create_deliveries.errors), 0)

    def test_create_delivery_can_be_processed(self):
        self.fake_version.delivery_formats = [self.fake_delivery_config]
        self.db.update_entity(self.fake_version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db,
            self.fake_project.name,
            self.fake_playlist.id,
            [self.fake_version.id],
        )

        create_deliveries = CreateDeliveries(
            data_model, test_mode=None, enforce_type_list=None
        )
        create_deliveries.is_valid()
        self.assertTrue(create_deliveries.can_be_processed())
        self.assertListEqual(create_deliveries.errors, [])
        self.assertEqual(
            create_deliveries.deliveries[0]._delivery_config.id,
            self.fake_delivery_config.id,
        )

    @mock.patch.object(ImageDelivery, "_generate_config_file")
    @mock.patch.object(ImageDelivery, "nuke_delivery_command")
    def test_create_delivery_job_priorities(
        self, config_file_mock, delivery_command_mock
    ):
        """
        Args:
            config_file_mock (mock.MagicMock):
            config_file_mock (mock.MagicMock):
        """
        config_file_mock.return_value = ""
        delivery_command_mock.return_value = ""
        list_to_test = [
            (DeliveryType.ONLINE, 65),
            (DeliveryType.OFFLINE, 65),
            (DeliveryType.FINAL, 45),
            (DeliveryType.WATERMARK, 45),
            (DeliveryType.DEFAULT, 45),
            (DeliveryType.OUTSOURCE, 45),
            (DeliveryType.INSOURCE, 45),
        ]
        for _type, priority in list_to_test:
            dc = self._create_fake_delivery_config(_type=_type)
            self.fake_version.delivery_formats = [dc]
            self.db.update_entity(self.fake_version, ["delivery_formats"])

            data_model = DeliveryDataModel(
                self.db,
                self.fake_project.name,
                self.fake_playlist.id,
                [self.fake_version.id],
            )

            create_deliveries = CreateDeliveries(data_model)
            create_deliveries.is_valid()
            for job in create_deliveries.get_all_farm_jobs():
                self.assertEqual(job.priority, priority)

    def test_create_delivery_can_be_processed_with_deprecated_online_field(self):
        fake_delivery = self._create_fake_delivery_config(_type=DeliveryType.ONLINE)

        # With Deprecated Field
        self.fake_version.delivery_formats_online = [fake_delivery]
        self.db.update_entity(self.fake_version, ["delivery_formats_online"])

        data_model = DeliveryDataModel(
            self.db,
            self.fake_project.name,
            self.fake_playlist.id,
            [self.fake_version.id],
        )

        create_deliveries = CreateDeliveries(
            data_model, test_mode=None, enforce_type_list=None
        )
        create_deliveries.is_valid()
        self.assertTrue(create_deliveries.can_be_processed())
        self.assertListEqual(create_deliveries.errors, [])
        self.assertEqual(
            create_deliveries.deliveries[0]._delivery_config.id, fake_delivery.id
        )
        # With new field
        self.fake_version.delivery_formats = [fake_delivery]
        self.db.update_entity(self.fake_version, ["delivery_formats"])

        data_model = DeliveryDataModel(
            self.db,
            self.fake_project.name,
            self.fake_playlist.id,
            [self.fake_version.id],
        )

        create_deliveries = CreateDeliveries(
            data_model, test_mode=None, enforce_type_list=None
        )
        create_deliveries.is_valid()
        self.assertTrue(create_deliveries.can_be_processed())
        self.assertListEqual(create_deliveries.errors, [])
        self.assertEqual(
            create_deliveries.deliveries[0]._delivery_config.id, fake_delivery.id
        )

    def test_create_delivery_check_published_files(self):
        fake_playlist = self._create_fake_playlist(code="test_published_files")

        self.create_test_published_file_type(
            DeliveryMovieItem.published_files_type().value
        )
        self.create_test_published_file_type(
            DeliveryImageSequenceItem.published_files_type().value
        )

        # two offline formats to ensure the tools will create published files for all configs
        offline_format = self._create_fake_delivery_config(
            _type=DeliveryType.OFFLINE, template="{Project.name}/{Shot.code}.mov"
        )
        other_offline_format = self._create_fake_delivery_config(
            _type=DeliveryType.OFFLINE,
            template="{Project.name}/{Shot.code}_{Version.code}.mxf",
        )
        online_format = self._create_fake_delivery_config(
            _type=DeliveryType.ONLINE,
            template="{Project.name}/{Shot.code}_{Version.code}_ONLINE.####.exr",
        )

        other_online_format = self._create_fake_delivery_config(
            _type=DeliveryType.ONLINE,
            template="{Project.name}/{Shot.code}_{Version.code}_OTHER_ONLINE.####.exr",
        )

        offline_image_sequence_format = self._create_fake_delivery_config(
            _type=DeliveryType.OFFLINE,
            template="{Project.name}/{Shot.code}_{Version.code}_OFFLINE.####.exr",
        )

        # update the delivery formats
        self.fake_version.delivery_formats = [offline_format, other_offline_format]
        self.fake_version.delivery_formats_online = [online_format, other_online_format]

        self.db.update_entity(
            self.fake_version, ["delivery_formats", "delivery_formats_online"]
        )

        # creating the offline delivery dm
        delivery_data_model = DeliveryDataModel(
            self.db, self.fake_project.name, fake_playlist.id, [self.fake_version.id]
        )

        create_deliveries = CreateDeliveries(
            delivery_data_model, test_mode=None, enforce_type_list=None
        )

        create_deliveries.is_valid()

        # forcing the data in the link for the test
        # this would normally be filled in at the delivery
        for delivery in create_deliveries.deliveries:
            delivery.version.link._database = self.db
            delivery.version.link.project = self.fake_project
            delivery.version.source_file_type = "exr"
            delivery.version.colorspace = "RGB"
            delivery.delivery_config.codec = "QT"
            delivery.delivery_config.fps = 24.0
            delivery.delivery_config.output_colorspace = "Rec709"

        # publishing a first version first to check that publishes are not overwritten
        create_deliveries._dm.publish_delivery(create_deliveries.deliveries[0])

        # publishing the deliveries
        create_deliveries._dm.publish_deliveries(create_deliveries.deliveries)

        sg_published_files = self.db.get_published_file_list(
            entity_list=[self.fake_shot]
        )
        sg_published_files_name = list()
        for sg_published_file in sg_published_files:
            sg_published_files_name.append(sg_published_file.name)

        expected_published_files_name = list()
        for delivery in create_deliveries.deliveries:
            expected_published_files_name.append(os.path.basename(delivery.output_path))

        self.assertListEqual(expected_published_files_name, sg_published_files_name)

    def test_published_file_in_other_version(self):
        # second version -> to check if the tool overwrites when the published files is in another version
        new_fake_version = Version()
        new_fake_version.code = "{}_NEW".format(self.fake_version.code)
        new_fake_version.link = self.fake_version.link
        new_fake_version.project = self.fake_project
        new_fake_version.created_by = self.fake_user
        new_fake_version = self.db.create_version(new_fake_version)

        fake_playlist = self._create_fake_playlist(
            code="test_published_files_in_other_version"
        )
        new_fake_playlist = self._create_fake_playlist(
            code="test_published_files_in_other_version_NEW"
        )

        self.create_test_published_file_type(
            DeliveryMovieItem.published_files_type().value
        )

        offline_format = self._create_fake_delivery_config(
            _type=DeliveryType.OFFLINE,
            template="/cool/path/the_same_name_for_everything.mov",
        )

        # update the delivery formats for both versions
        self.fake_version.delivery_formats = [offline_format]
        new_fake_version.delivery_formats = [offline_format]

        self.db.update_entity(self.fake_version, ["delivery_formats"])
        self.db.update_entity(new_fake_version, ["delivery_formats"])

        # creating the offline delivery dm for first version
        delivery_data_model_first_version = DeliveryDataModel(
            self.db, self.fake_project.name, fake_playlist.id, [self.fake_version.id]
        )

        create_deliveries_first_version = CreateDeliveries(
            delivery_data_model_first_version, test_mode=None, enforce_type_list=None
        )

        create_deliveries_first_version.is_valid()

        # forcing the data in the link for the test
        # this would normally be filled in at the delivery
        for delivery in create_deliveries_first_version.deliveries:
            delivery.version.link._database = self.db
            delivery.version.link.project = self.fake_project
            delivery.version.source_file_type = "exr"
            delivery.version.colorspace = "RGB"
            delivery.delivery_config.codec = "QT"
            delivery.delivery_config.fps = 24.0
            delivery.delivery_config.output_colorspace = "Rec709"

        # publishing the delivery
        create_deliveries_first_version._dm.publish_deliveries(
            create_deliveries_first_version.deliveries
        )

        # creating the offline delivery dm for the second version -> should overwrite published file of first version
        delivery_data_model_second_version = DeliveryDataModel(
            self.db, self.fake_project.name, new_fake_playlist.id, [new_fake_version.id]
        )

        create_deliveries_second_version = CreateDeliveries(
            delivery_data_model_second_version, test_mode=None, enforce_type_list=None
        )

        create_deliveries_second_version.is_valid()

        # forcing the data in the link for the test
        # this would normally be filled in at the delivery
        for delivery in create_deliveries_second_version.deliveries:
            delivery.version.link._database = self.db
            delivery.version.link.project = self.fake_project
            delivery.version.source_file_type = "exr"
            delivery.version.colorspace = "RGB"
            delivery.delivery_config.codec = "QT"
            delivery.delivery_config.fps = 24.0
            delivery.delivery_config.output_colorspace = "Rec709"

        # publishing the deliveries
        create_deliveries_second_version._dm.publish_deliveries(
            create_deliveries_second_version.deliveries
        )

        # get the versions
        updated_fake_version = self.db.get_version(self.fake_version.id)
        updated_new_fake_version = self.db.get_version(new_fake_version.id)

        # check that first version has no published files
        self.assertEqual(len(updated_fake_version.published_files), 0)

        # check that there is a published file in second versions
        self.assertEqual(len(updated_new_fake_version.published_files), 1)

        # check that it's the right name
        self.assertEqual(
            updated_new_fake_version.published_files[0].name,
            "the_same_name_for_everything.mov",
        )

        # check that it's the right path
        self.assertEqual(
            updated_new_fake_version.published_files[0].path,
            "/cool/path/the_same_name_for_everything.mov",
        )


if __name__ == "__main__":
    unittest.main()
