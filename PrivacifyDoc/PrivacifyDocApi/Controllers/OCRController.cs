using Microsoft.AspNetCore.Mvc;
using PrivacifyDoc.CQRS.Dispatcher;

namespace PrivacifyDoc.Controllers;

public class OCRController : Controller
{
    private readonly Dispatcher _dispatcher;

    public OCRController(Dispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    [HttpPost]
    public IActionResult CreateOrder( /*..*/)
    {
        var command = new CreateOrderCommand( /*..*/);
        _dispatcher.Send(command);
        // ...
    }

    [HttpGet]
    public IActionResult GetOrder(int id)
    {
        var query = new GetOrderByIdQuery { id = id };
        var result = _dispatcher.Query<Order>(query);
        // ...
    }
}