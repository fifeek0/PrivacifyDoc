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
        // Locate the correct handler and invoke it
    }
}