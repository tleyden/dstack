"""empty message

Revision ID: 09228dca524f
Revises: 842d9dab4d43
Create Date: 2023-08-30 10:48:28.215451

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "09228dca524f"
down_revision = "842d9dab4d43"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "jobs",
        sa.Column("job_id", sa.String(length=50), nullable=False),
        sa.Column("run_name", sa.String(length=50), nullable=True),
        sa.Column("project_name", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("job_data", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_name"],
            ["projects.name"],
            name=op.f("fk_jobs_project_name_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("job_id", name=op.f("pk_jobs")),
    )
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_jobs_run_name"), ["run_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_jobs_status"), ["status"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_jobs_status"))
        batch_op.drop_index(batch_op.f("ix_jobs_run_name"))

    op.drop_table("jobs")
    # ### end Alembic commands ###