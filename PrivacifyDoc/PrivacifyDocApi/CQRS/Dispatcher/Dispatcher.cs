using System.Windows.Input;

namespace PrivacifyDoc.CQRS.Dispatcher;

public class Dispatcher
{
    public void Send<T>(T command) where T : ICommand
    {
        // Locate the correct handler and invoke it
    }

    public TResult Query<TResult>(IQuery<TResult> query)
    {
        if (query == null) throw new ArgumentNullException(nameof(query));

        var handlerType = typeof(IQueryHandler<,>).MakeGenericType(query.GetType(), typeof(TResult));

        object handler = null; // Get handler object using dependency injection or service locator

        if (handler == null) throw new DispatcherException($"No handler registered for {nameof(query)}");

        var handlerMethod = handlerType.GetMethod("Handle");

        if (handlerMethod == null) throw new DispatcherException($"No Handle method found for {nameof(query)}");

        return (TResult)handlerMethod.Invoke(handler, new object[] { query });
    }
}