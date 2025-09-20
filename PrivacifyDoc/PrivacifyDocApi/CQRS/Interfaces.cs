using System.Threading;
using System.Threading.Tasks;

namespace PrivacifyDoc.Api.CQRS
{
    public interface ICommand { }

    public interface IQuery<out TResult> { }

    public interface ICommandHandler<in TCommand> where TCommand : ICommand
    {
        Task HandleAsync(TCommand command, CancellationToken cancellationToken = default);
    }

    public interface IQueryHandler<in TQuery, TResult> where TQuery : IQuery<TResult>
    {
        Task<TResult> HandleAsync(TQuery query, CancellationToken cancellationToken = default);
    }
}
