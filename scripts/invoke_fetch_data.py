import typer

from solar_predictor.handlers.fetch_data import lambda_handler


def main(
    lat: str = typer.Option(..., help="Latitude"),
    long: str = typer.Option(..., help="Longitude"),
    start_date: str | None = typer.Option(None, help="YYYY-MM-DD"),
    end_date: str | None = typer.Option(None, help="YYYY-MM-DD"),
):
    event = {
        "lat": lat,
        "long": long,
        "start_date": start_date,
        "end_date": end_date,
    }
    res = lambda_handler(event, {})
    print(res)


if __name__ == "__main__":
    typer.run(main)
