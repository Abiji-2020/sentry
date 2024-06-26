from ..base import ModelDeletionTask, ModelRelation


class CommitAuthorDeletionTask(ModelDeletionTask):
    def get_child_relations(self, instance):
        from sentry.models.commit import Commit

        return [
            ModelRelation(Commit, {"author_id": instance.id}),
        ]
