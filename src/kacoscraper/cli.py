from dataclasses import asdict
import logging
import pprint
import click
from kacoscraper import prometheus
from kacoscraper.livedata import (
    InverterDataProvider,
    KacoNX3InverterDataProvider,
    get_inverter_details,
    get_inverters,
)


@click.group
@click.pass_context
@click.option("-h", "--host", default="kaco.fritz.box")
@click.option("-v", "--verbose", count=True)
def kaco_cli(ctx: click.Context, host: str, verbose: int) -> None:
    ctx.obj = {"host": host}
    match verbose:
        case 0:
            level = logging.WARNING
        case 1:
            level = logging.INFO
        case _:
            level = logging.DEBUG
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=level)


@kaco_cli.command("call")
@click.argument("path")
@click.pass_context
def call_kaco(ctx: click.Context, path: str) -> None:
    host = ctx.obj["host"]
    response = call_kaco(host, path)
    print(response)


@kaco_cli.command("live")
@click.option("-d", "--details/--no-details", default=True)
@click.pass_context
def get_live_data(ctx: click.Context, details: bool) -> None:
    inverters = get_inverters(ctx.obj["host"])
    for inverter in inverters:
        if details:
            inverter_details = get_inverter_details(ctx.obj["host"], inverter.serial)
            pprint.pprint(asdict(inverter_details))
        else:
            print(
                f"{inverter.serial}: total {inverter.energy_total_kwh}kWh; current {inverter.power_ac_watts}W"
            )


@kaco_cli.command("serve")
@click.option("-p", "--port", type=int, default=8007)
@click.pass_context
def poll(ctx: click.Context, port: int) -> None:
    inverters = get_inverters(ctx.obj["host"])

    providers: list[InverterDataProvider] = [
        KacoNX3InverterDataProvider(host=ctx.obj["host"], serial=inverter.serial)
        for inverter in inverters
    ]
    prometheus.poll(providers, port)

if __name__ == "__main__":
    kaco_cli()