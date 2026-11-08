import argparse
from datetime import date
from pathlib import Path
from .core import initialize, plan_product, save_plan, boundaries
from .workflows import THEMES, products


def main():
    p=argparse.ArgumentParser(description='Bangladesh thematic Earth Engine exports')
    p.add_argument('theme', choices=THEMES)
    p.add_argument('--start',default='2024-01-01')
    p.add_argument('--end',default='2025-01-01')
    p.add_argument('--authenticate',action='store_true')
    p.add_argument('--submit',action='store_true', help='Start export tasks; default only saves a task plan')
    p.add_argument('--admin-level',type=int,choices=(0,1,2),default=2)
    args=p.parse_args()
    if date.fromisoformat(args.start)>=date.fromisoformat(args.end):p.error('start must precede end')
    initialize(args.authenticate)
    country, units=boundaries(args.admin_level)
    counts={'country':country.size().getInfo(),'admin_units':units.size().getInfo()}
    if not counts['country'] or not counts['admin_units']:raise RuntimeError(f'Empty boundary selection: {counts}')
    tasks=[]
    for product in products(args.theme,args.start,args.end):
        # Evaluate bands and a coarse representative reduction before allowing submission.
        if not product.image.bandNames().getInfo():raise RuntimeError(f'Empty image: {product.name}')
        tasks.extend(plan_product(product,args.theme,args.start+'_'+args.end,args.admin_level))
    out=Path('outputs')/args.theme/'task_plan.json'
    save_plan(tasks,out)
    if args.submit:
        for task in tasks:
            try:
                task.start()
            finally:
                save_plan(tasks,out)  # retain IDs even if a later submission fails
            print(task.id, task.config.get('description'))
        save_plan(tasks,out)
    print(f'{len(tasks)} export tasks; {counts}; plan: {out}; submitted: {args.submit}')


if __name__=='__main__':main()
