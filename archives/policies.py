class ArchivePolicy(object):
    """
    Base ArchivePolicy class. Gets artifact URLs from a build,
    maps them to paths for archiving.
    """
    def __init__(self, projectbuild):
        self.projectbuild = projectbuild

    def get_mapped_path(self, artifact):
        """
        Returns the mapped path for the artifact url.

        Override this with your archive specific mapping.
        """
        return artifact.url

    def get_mappings(self):
        """
        Returns a dictionary of artifact_url:mapped_path.
        """
        paths = {}
        for artifact in self.projectbuild.get_current_artifacts():
            paths[artifact.url] = self.get_mapped_path(artifact)
        return paths


class CdimageArchivePolicy(ArchivePolicy):
    """
    Converts jenkins artifact urls to a cdimage-like structure.
    """
    def get_mapped_path(self, artifact):
        """
        Returns a cdimage-like relative path.
        """
        return "{project}/{build_id}/{filename}".format(
            **{
                "project": self.projectbuild.project.name,
                "build_id": self.projectbuild.build_id,
                "filename": artifact.filename
            })
