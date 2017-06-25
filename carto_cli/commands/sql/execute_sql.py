import click
import json

@click.command(help="Execute a SQL passed as a string")
@click.option('-f','--format',default="csv",help="Format of your results",
    type=click.Choice(['csv', 'shp','json','gpkg','geojson']))
@click.option('-o','--output',type=click.File('wb'),
              help="Output file to generate instead of printing directly")
@click.option('-e','--explain',is_flag=True,default=False,help="Explains the query")
@click.option('-ea','--explain-analyze',is_flag=True,default=False,help="Explains the query executing it")
@click.help_option('-h', '--help')
@click.argument('sql', nargs=-1)
@click.pass_context
def run(ctx,format,output,explain,explain_analyze,sql):
    carto_obj = ctx.obj['carto']
    sql = ' '.join(sql)
    try:
        if explain:
            sql = "EXPLAIN " + sql
            format = 'json'
        elif explain_analyze:
            sql = "EXPLAIN ANALYZE " + sql
            format = 'json'

        result = carto_obj.execute_sql(sql,format=format,do_post=True)

        if explain or explain_analyze:
            result = '\r\n'.join([row['QUERY PLAN'] for row in result['rows']])
        elif format in ['json','geojson']:
            result = json.dumps(result)

        if output:
            output.write(result)
        else:
            click.echo(result,nl=format=='json')
    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))


@click.command(help="Kills a query based on its pid")
@click.argument('pid',type=int)
@click.help_option('-h', '--help')
@click.pass_context
def kill(ctx,pid):
    carto_obj = ctx.obj['carto']
    sql = '''SELECT pg_cancel_backend({})
from pg_stat_activity where usename=current_user;'''.format(pid)

    try:
        result = carto_obj.execute_sql(sql)
        if 'rows' in result and len(result['rows']) > 0:
            cancelling = result['rows'][0]['pg_cancel_backend']

            if cancelling:
                click.echo('Query cancelled')
            else:
                ctx.fail('Invalid PID?')
        else:
            ctx.fail("Error cancelling the query")
    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))
