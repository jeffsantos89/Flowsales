"""Enhanced initial schema creation for AI Service"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import expression

# Alembic revision identifiers
revision = "202310101007"
down_revision = "202310101006"  # Certifique-se que existe uma revisão anterior
branch_labels = None
depends_on = None

def upgrade():
    """Creates enhanced schema for AI-SERVICE with security, constraints, and indexing"""

    # Verifica a versão do banco antes de executar
    connection = op.get_bind()
    result = connection.execute("SELECT current_setting('server_version_num')")
    db_version = int(result.scalar())

    if db_version < 120000:
        raise RuntimeError("PostgreSQL 12+ required for this migration.")

    # Create extensions if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Create custom types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('admin', 'user', 'analyst');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum('admin', 'user', 'analyst', name='user_role'), nullable=False, server_default='user'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=expression.true()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("login_attempts", sa.Integer, nullable=False, server_default='0'),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('email ~* \'^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$\'', name='email_format_check'),
        schema="public"
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])

    # Predictions table
    op.create_table(
        "predictions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("input_data", JSONB, nullable=False),
        sa.Column("prediction_result", JSONB, nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("processing_time", sa.Float, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default='completed'),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='confidence_score_check'),
        schema="public"
    )
    op.create_index("ix_predictions_user_created", "predictions", ["user_id", "created_at"])
    op.create_index("ix_predictions_status", "predictions", ["status"])

    # AI Models table
    op.create_table(
        "ai_models",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("version", sa.VARCHAR(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("configuration", JSONB, nullable=True),
        sa.Column("metrics", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("public.users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("model_name", "version", name="uq_ai_models_name_version"),
        schema="public"
    )
    op.create_index("ix_ai_models_status", "ai_models", ["status"])

def downgrade():
    """Rollback with exception handling"""
    try:
        op.drop_index("ix_ai_models_status")
        op.drop_constraint("uq_ai_models_name_version", "ai_models", schema="public", type_="unique")
        op.drop_table("ai_models", schema="public")

        op.drop_index("ix_predictions_status")
        op.drop_index("ix_predictions_user_created")
        op.drop_table("predictions", schema="public")

        op.drop_index("ix_users_deleted_at")
        op.drop_index("ix_users_email")
        op.drop_table("users", schema="public")

        op.execute("DROP TYPE IF EXISTS user_role")

    except Exception as e:
        print(f"Error during downgrade: {str(e)}")
        raise
