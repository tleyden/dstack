package lambda

import (
	"context"
	"io"
	"os"

	"github.com/docker/docker/api/types/mount"
	"gopkg.in/yaml.v2"

	"github.com/dstackai/dstack/runner/internal/backend"
	"github.com/dstackai/dstack/runner/internal/backend/base"
	"github.com/dstackai/dstack/runner/internal/docker"
	"github.com/dstackai/dstack/runner/internal/gerrors"
	"github.com/dstackai/dstack/runner/internal/log"
	"github.com/dstackai/dstack/runner/internal/models"
)

type LambdaConfig struct {
	ApiKey string `yaml:"api_key"`
}

type LambdaBackend struct {
	storageBackend backend.Backend
	apiClient      *LambdaAPIClient
}

func init() {
	backend.RegisterBackend(
		"lambda",
		func(ctx context.Context, pathConfig string, primaryBackend *backend.Backend) (backend.Backend, error) {
			if primaryBackend == nil {
				return nil, gerrors.New("primaryBackend cannot be nil")
			}
			config := LambdaConfig{}
			log.Trace(ctx, "Read config file", "path", pathConfig)
			fileContent, err := os.ReadFile(pathConfig)
			if err != nil {
				return nil, gerrors.Wrap(err)
			}
			log.Trace(ctx, "Unmarshal config")
			err = yaml.Unmarshal(fileContent, &config)
			if err != nil {
				return nil, gerrors.Wrap(err)
			}
			return New(config, *primaryBackend), nil
		},
	)
}

func New(config LambdaConfig, primaryBackend backend.Backend) *LambdaBackend {
	// _ = os.Setenv("AWS_ACCESS_KEY_ID", config.StorageConfig.Credentials.AccessKey)
	// _ = os.Setenv("AWS_SECRET_ACCESS_KEY", config.StorageConfig.Credentials.SecretKey)
	return &LambdaBackend{
		storageBackend: primaryBackend,
		apiClient:      NewLambdaAPIClient(config.ApiKey),
	}
}

func (l *LambdaBackend) Init(ctx context.Context, ID string) error {
	return l.storageBackend.Init(ctx, ID)
}

func (l *LambdaBackend) Job(ctx context.Context) *models.Job {
	return l.storageBackend.Job(ctx)
}

func (l *LambdaBackend) RefetchJob(ctx context.Context) (*models.Job, error) {
	return l.storageBackend.RefetchJob(ctx)
}

func (l *LambdaBackend) UpdateState(ctx context.Context) error {
	return l.storageBackend.UpdateState(ctx)
}

func (l *LambdaBackend) IsInterrupted(ctx context.Context) (bool, error) {
	return false, nil
}

func (l *LambdaBackend) Stop(ctx context.Context) error {
	return nil
}

func (l *LambdaBackend) Shutdown(ctx context.Context) error {
	return l.apiClient.TerminateInstance(ctx, []string{l.storageBackend.Job(ctx).RequestID})
}

func (l *LambdaBackend) GetArtifact(ctx context.Context, runName, localPath, remotePath string, mount bool) base.Artifacter {
	return l.storageBackend.GetArtifact(ctx, runName, localPath, remotePath, mount)
}

func (l *LambdaBackend) GetCache(ctx context.Context, runName, localPath, remotePath string) base.Artifacter {
	return l.storageBackend.GetCache(ctx, runName, localPath, remotePath)
}

func (l *LambdaBackend) Requirements(ctx context.Context) models.Requirements {
	return l.storageBackend.Requirements(ctx)
}

func (l *LambdaBackend) MasterJob(ctx context.Context) *models.Job {
	return l.storageBackend.MasterJob(ctx)
}

func (l *LambdaBackend) CreateLogger(ctx context.Context, logGroup, logName string) io.Writer {
	return l.storageBackend.CreateLogger(ctx, logGroup, logName)
}

func (l *LambdaBackend) ListSubDir(ctx context.Context, dir string) ([]string, error) {
	return l.storageBackend.ListSubDir(ctx, dir)
}

func (l *LambdaBackend) GetJobByPath(ctx context.Context, path string) (*models.Job, error) {
	return l.storageBackend.GetJobByPath(ctx, path)
}

func (l *LambdaBackend) Bucket(ctx context.Context) string {
	return l.storageBackend.Bucket(ctx)
}

func (l *LambdaBackend) Secrets(ctx context.Context) (map[string]string, error) {
	return l.storageBackend.Secrets(ctx)
}

func (l *LambdaBackend) GitCredentials(ctx context.Context) *models.GitCredentials {
	return l.storageBackend.GitCredentials(ctx)
}

func (l *LambdaBackend) GetRepoDiff(ctx context.Context, path string) (string, error) {
	return l.storageBackend.GetRepoDiff(ctx, path)
}

func (l *LambdaBackend) GetRepoArchive(ctx context.Context, path, dir string) error {
	return l.storageBackend.GetRepoArchive(ctx, path, dir)
}

func (l *LambdaBackend) GetBuildDiffInfo(ctx context.Context, spec *docker.BuildSpec) (*base.StorageObject, error) {
	obj, err := l.storageBackend.GetBuildDiffInfo(ctx, spec)
	if err != nil {
		return nil, gerrors.Wrap(err)
	}
	return obj, nil
}

func (l *LambdaBackend) GetBuildDiff(ctx context.Context, key, dst string) error {
	return l.storageBackend.GetBuildDiff(ctx, key, dst)
}

func (l *LambdaBackend) PutBuildDiff(ctx context.Context, src string, spec *docker.BuildSpec) error {
	return l.storageBackend.PutBuildDiff(ctx, src, spec)
}

func (l *LambdaBackend) GetTMPDir(ctx context.Context) string {
	return l.storageBackend.GetTMPDir(ctx)
}

func (l *LambdaBackend) GetDockerBindings(ctx context.Context) []mount.Mount {
	return l.storageBackend.GetDockerBindings(ctx)
}
